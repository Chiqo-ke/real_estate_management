from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta, datetime
from ..database import get_db
from ..services.auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from ..schemas.auth import Token, TenantCreate

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Query tenant from database
    tenant = db.execute(
        text("SELECT tenant_id, email, password FROM tenants WHERE email = :email"),
        {"email": form_data.username}
    ).fetchone()
    
    if not tenant or not verify_password(form_data.password, tenant.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": tenant.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_tenant = db.execute(
        text("SELECT email FROM tenants WHERE email = :email"),
        {"email": tenant.email}
    ).fetchone()
    
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify property exists and has available units
    property_check = db.execute(
        text("SELECT available_units FROM properties WHERE property_id = :property_id"),
        {"property_id": tenant.lease_details.property_id}
    ).fetchone()
    
    if not property_check or property_check.available_units <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property not available"
        )

    try:
        # Start transaction
        db.execute(text("BEGIN"))
        
        # Insert tenant
        hashed_password = get_password_hash(tenant.password)
        tenant_result = db.execute(
            text("""
                INSERT INTO tenants (first_name, last_name, email, password, phone, 
                                   emergency_contact_name, emergency_contact_phone,
                                   identification_type, identification_number)
                VALUES (:first_name, :last_name, :email, :password, :phone,
                        :emergency_contact_name, :emergency_contact_phone,
                        :identification_type, :identification_number)
            """),
            {
                "first_name": tenant.first_name,
                "last_name": tenant.last_name,
                "email": tenant.email,
                "password": hashed_password,
                "phone": tenant.phone,
                "emergency_contact_name": tenant.emergency_contact_name,
                "emergency_contact_phone": tenant.emergency_contact_phone,
                "identification_type": tenant.identification_type,
                "identification_number": tenant.identification_number
            }
        )
        tenant_id = tenant_result.lastrowid
        
        # Create lease
        lease_result = db.execute(
            text("""
                INSERT INTO leases (property_id, tenant_id, unit_number, start_date,
                                  end_date, monthly_rent, security_deposit, lease_status)
                VALUES (:property_id, :tenant_id, :unit_number, :start_date,
                        :end_date, :monthly_rent, :security_deposit, 'Active')
            """),
            {
                "property_id": tenant.lease_details.property_id,
                "tenant_id": tenant_id,
                "unit_number": tenant.lease_details.unit_number,
                "start_date": tenant.lease_details.start_date,
                "end_date": tenant.lease_details.end_date,
                "monthly_rent": tenant.lease_details.monthly_rent,
                "security_deposit": tenant.lease_details.security_deposit
            }
        )
        lease_id = lease_result.lastrowid
        
        # Create first invoice (security deposit + first month rent)
        total_amount = tenant.lease_details.security_deposit + tenant.lease_details.monthly_rent
        invoice_result = db.execute(
            text("""
                INSERT INTO invoices (lease_id, invoice_date, due_date, amount, 
                                    description, status)
                VALUES (:lease_id, CURRENT_DATE, CURRENT_DATE, :amount,
                        'Security deposit and first month rent', 'Pending')
            """),
            {
                "lease_id": lease_id,
                "amount": total_amount
            }
        )
        
        # Update available units
        db.execute(
            text("""
                UPDATE properties 
                SET available_units = available_units - 1 
                WHERE property_id = :property_id
            """),
            {"property_id": tenant.lease_details.property_id}
        )
        
        db.execute(text("COMMIT"))
        
        return {
            "message": "Tenant registered successfully",
            "tenant_id": tenant_id,
            "lease_id": lease_id
        }
        
    except Exception as e:
        db.execute(text("ROLLBACK"))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
