from asyncio.log import logger
from typing import Optional
from fastapi_limiter.depends import RateLimiter
from fastapi import  APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, timedelta
from src.database.db import get_db

from src.schemas.schemas import ContactResponse, ContactCreate
from src.models.models import Contact, User
from sqlalchemy import extract

from src.repository.repository import get_contacts, get_contact
from src.utils.dependencies import get_current_user

router = APIRouter()

@router.post("/contacts/", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["contacts"],status_code=status.HTTP_201_CREATED)
async def create_contact(contact_data: ContactCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Creates a new contact for the currently authenticated user.

    This endpoint allows the user to create a new contact by providing contact details. The contact
    is associated with the authenticated user.

    :param contact_data: The contact details (name, email, phone, etc.) to be added.
    :type contact_data: ContactCreate
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The newly created contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact creation fails or the user is unauthorized.
    """
    new_contact = Contact(**contact_data.dict(), user_id=current_user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact

@router.get("/contacts/", response_model=list[ContactResponse],dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["contacts"])
async def read_contacts(limit: int = 10, offset: int = 0, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Retrieves a list of contacts for the currently authenticated user.

    This endpoint returns the user's contacts with pagination support. The user can specify
    the number of contacts to return (`limit`) and the starting point (`offset`).

    :param limit: The number of contacts to retrieve (default is 10).
    :type limit: int
    :param offset: The offset from which to start retrieving contacts (default is 0).
    :type offset: int
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of the user's contacts.
    :rtype: list[ContactResponse]
    :raises HTTPException: If there is an issue with retrieving the contacts.
    """
    return await get_contacts(db, user_id=current_user.id, limit=limit, offset=offset)


@router.get("/contacts/{contact_id}", response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["contacts"])
async def read_contact(contact_id: int, current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    """
    Retrieves a specific contact by its ID for the currently authenticated user.

    This endpoint returns details of a specific contact associated with the authenticated user.
    If the contact is not found or does not belong to the user, a 404 error is returned.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The requested contact details.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found or does not belong to the user.
    """
    db_contact = await get_contact(contact_id, current_user, db)
    if db_contact is None or db_contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["contacts"])
async def update_contact_(
    contact_id: int,
    contact: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Updates an existing contact for the currently authenticated user.

    This endpoint allows the user to update an existing contact's details. The contact is identified
    by its ID and updated with the new data provided. The contact must belong to the authenticated user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The new contact details.
    :type contact: ContactCreate
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found or the user is unauthorized.
    """

    db_contact = await get_contact(contact_id, current_user, db)


    if db_contact is None or db_contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")


    for key, value in contact.dict().items():
        setattr(db_contact, key, value)


    try:
        await db.commit()
        await db.refresh(db_contact)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error {contact_id} for {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Error update contact")

    return db_contact

async def get_contact(contact_id: int, user: User, db: AsyncSession):
    """
    Retrieves a specific contact by its ID for the currently authenticated user.

    This function checks if the contact exists and belongs to the currently authenticated user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The currently authenticated user.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The contact if found and belongs to the user, otherwise None.
    :rtype: Optional[Contact]
    :raises: Logs an error if the contact retrieval fails.
    """
    try:
        query = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error  {contact_id} for {user.id}: {e}")
        return None

@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["contacts"])
async def delete_contact_(contact_id: int, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    """
    Deletes a contact for the currently authenticated user.

    This endpoint deletes a contact identified by its ID, provided it belongs to the authenticated user.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A 204 No Content status code on successful deletion.
    :rtype: None
    :raises HTTPException: If the contact is not found or the user is unauthorized.
    """
    db_contact = await get_contact(contact_id, current_user, db)
    if db_contact is None or db_contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")

    await db.delete(db_contact)
    await db.commit()

@router.get("/contacts/search/", response_model=list[ContactResponse],dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["contacts"])
async def search_contacts(
        first_name: Optional[str] = Query(None),
        last_name: Optional[str] = Query(None),
        email: Optional[str] = Query(None),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Searches for contacts based on optional filters (first name, last name, or email).

    This endpoint allows the user to search for contacts that match the provided filters (first name,
    last name, or email). All contacts belong to the authenticated user.

    :param first_name: The first name of the contact to search for (optional).
    :type first_name: Optional[str]
    :param last_name: The last name of the contact to search for (optional).
    :type last_name: Optional[str]
    :param email: The email address of the contact to search for (optional).
    :type email: Optional[str]
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of contacts that match the search criteria.
    :rtype: list[ContactResponse]
    """
    query = select(Contact).filter(Contact.user_id == current_user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/contacts/birthdays/", response_model=list[ContactResponse],dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["contacts"])
async def get_upcoming_birthdays(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Retrieves contacts with upcoming birthdays within the next 7 days for the currently authenticated user.

    This endpoint returns contacts that have birthdays coming up within the next 7 days, based on the
    current date. The user must be authenticated.

    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of contacts with birthdays within the next 7 days.
    :rtype: list[ContactResponse]
    """
    today = date.today()
    upcoming_date = today + timedelta(days=7)
    query = select(Contact).filter( Contact.user_id == current_user.id,
    ((extract('month', Contact.birthday) == today.month) &(extract('day', Contact.birthday) >= today.day)) | ((extract('month', Contact.birthday) == upcoming_date.month) & (extract('day', Contact.birthday) <= upcoming_date.day)))

    result = await db.execute(query)
    return result.scalars().all()