import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Contact, User
from src.repository.repository import get_contacts,get_contact,update_contact,update_avatar_url,get_user_by_email,delete_contact,confirmed_email
from src.schemas.schemas import  ContactCreate


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, username='test_user', hashed_password='qwerty', confirmed=True)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, title='test_title_1', description='test_description_1', user_id=self.user.id),
            Contact(id=2, title='test_title_2', description='test_description_2', user_id=self.user.id),
        ]

        mocked_scalars = MagicMock()
        mocked_scalars.all.return_value = contacts
        mocked_result = MagicMock()
        mocked_result.scalars.return_value = mocked_scalars
        self.session.execute.return_value = mocked_result

        result = await get_contacts(self.session, self.user.id,limit, offset)

        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact= Contact(id=1, title='test_title_1', description='test_description_1', user_id=self.user.id)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_result

        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_not_found(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_result

        result = await get_contact(contact_id=1, user=self.user, db=self.session)

        self.assertIsNone(result)

    async def test_delete_contact(self):
        contact= Contact(id=1, title='test_title_1', description='test_description_1', user_id=self.user.id)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_result

        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_result


        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            title='old_title',
            description='old_description',
            user_id=self.user.id
        )
        self.session.execute.return_value = mocked_contact

        contact = ContactCreate(
                first_name='updated_first_name',
                last_name='updated_last_name',
                email='updated_email@test.com',
                phone_number='123456789',
                birthday='2000-01-01',
                additional_data='Updated data'
            )

        result = await update_contact(contact_id=1, contact=contact, user=self.user, db=self.session)

        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, 'updated_first_name')
        self.assertEqual(result.last_name, 'updated_last_name')
        self.assertEqual(result.email, 'updated_email@test.com')


    async def test_confirmed_email(self):
        email = "test@example.com"
        user = MagicMock(spec=User)
        user.email = email
        user.confirmed = False

        mock_get_user_by_email = AsyncMock(return_value=user)

        db_session = MagicMock()
        db_session.commit = AsyncMock()

        with unittest.mock.patch("src.repository.repository.get_user_by_email", mock_get_user_by_email):
            await confirmed_email(email, db_session)

        self.assertTrue(user.confirmed)
        db_session.commit.assert_awaited_once()



    async def test_get_user_by_email(self):
        email = "test@example.com"
        user = MagicMock(spec=User)
        user.email = email

        mock_scalars= MagicMock()
        mock_scalars.first.return_value=user
        mock_result= MagicMock()
        mock_result.scalars.return_value = mock_scalars
        self.session.execute.return_value = mock_result

        result = await get_user_by_email(email, self.session)

        self.assertEqual(result, user)
        self.session.execute.assert_awaited_once()



    async def test_update_avatar_url(self):
        email = "test@example.com"
        new_avatar_url = "http://example.com/new_avatar.jpg"
        user = MagicMock(spec=User)
        user.email = email
        user.avatar = None

        db_session = MagicMock()
        db_session.execute = AsyncMock(return_value=MagicMock())
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()

        result = await update_avatar_url(email, new_avatar_url, db_session)

        self.assertEqual(result.avatar, new_avatar_url)
        db_session.commit.assert_awaited_once()
        db_session.refresh.assert_awaited_once()


