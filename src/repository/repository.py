from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.models import Contact, User
from src.schemas.schemas import ContactCreate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def get_user_by_email(email: str, db: AsyncSession):
    """
    Retrieves a user from the database by their email address.

    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The user object if found, otherwise None.
    :rtype: User
    """
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()

async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Marks a user's email as confirmed in the database.

    :param email: The email address of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: None
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()

async def get_contacts(db: AsyncSession, user_id: int, limit: int = 10, offset: int = 0):
    """
    Retrieves a list of contacts for a specific user with optional pagination.

    :param db: The database session.
    :type db: AsyncSession
    :param user_id: The ID of the user whose contacts are to be retrieved.
    :type user_id: int
    :param limit: The maximum number of contacts to retrieve. Defaults to 10.
    :type limit: int
    :param offset: The number of contacts to skip before retrieving. Defaults to 0.
    :type offset: int
    :return: A list of contacts belonging to the specified user.
    :rtype: List[Contact]
    """
    query = select(Contact).filter(Contact.user_id == user_id).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_contact(contact_id: int, user: User, db: AsyncSession):
    """
    Retrieves a contact for a user by its ID.

    :param db: The database session.
    :type db: AsyncSession
    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user requesting the contact.
    :type user: User
    :return: The contact object if found, otherwise None.
    :rtype: Optional[Contact]
    :raises: Logs an error if an exception occurs during the database operation.
    """
    try:
        query = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error {contact_id} for {user.id}: {e}")
        return None

async def update_contact(contact_id: int, contact: ContactCreate, user: User, db: AsyncSession):
    """
    Updates an existing contact for a user with new data.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The new contact data to update.
    :type contact: ContactCreate
    :param user: The user who owns the contact.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated contact object if successful, otherwise None.
    :rtype: Optional[Contact]
    :raises: Logs an error if an exception occurs during the database operation.
    """
    try:
        db_contact = await get_contact(contact_id, user, db)
        if db_contact:
            for key, value in contact.dict().items():
                setattr(db_contact, key, value)
            await db.commit()
            await db.refresh(db_contact)
            return db_contact
        else:
            logger.warning(f"Contact {contact_id} not found for {user.id}")
            return None
    except Exception as e:
        logger.error(f"Error {contact_id} for {user.id}: {e}")
        return None

async def delete_contact(contact_id: int, user: User, db: AsyncSession):
    """
    Removes a contact for a user based on the contact ID.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user who owns the contact.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The removed contact object if successful, otherwise None.
    :rtype: Optional[Contact]
    :raises: Logs an error if an exception occurs during the database operation.
    """
    try:
        db_contact = await get_contact(contact_id, user, db)
        if db_contact:
            await db.delete(db_contact)
            await db.commit()
            return db_contact
        else:
            logger.warning(f"Contact  {contact_id} not founf for {user.id}")
            return None
    except Exception as e:
        logger.error(f"Error  {contact_id} for {user.id}: {e}")
        return None

async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Updates the avatar URL for a user based on their email.

    :param email: The email of the user whose avatar URL needs to be updated.
    :type email: str
    :param url: The new avatar URL to be set, or None to clear the avatar.
    :type url: str | None
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated user object.
    :rtype: User
    :raises HTTPException: If the user with the given email is not found.
    """
    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
