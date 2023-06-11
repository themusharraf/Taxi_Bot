from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.default import skip, button_1234, treaty, region, make_district, accept_or_not
from states import ClientState
from utils.misc import region_list, get_districts_by_region

order_taxi_router = Router()

######################################################
#                  Handlers
######################################################

@order_taxi_router.message(ClientState.from_region)
async def process_from_region(message: Message, state: FSMContext):
    if message.text not in region_list:
        return await message.answer("❗️ Viloyat tanlashda xatolik yuz berdi, iltimos quyidagi viloyatlardan birini tanlang!") # noqa
    await state.update_data(from_region=message.text)
    await state.set_state(ClientState.from_district)
    await message.answer("❗️ Tumanni tanlang", reply_markup=make_district(message.text).as_markup(resize_keyboard=True))


@order_taxi_router.message(ClientState.from_district)
async def process_from_district(message: Message, state: FSMContext):
    region_name = (await state.get_data())['from_region']
    if message.text not in get_districts_by_region(region_name):
        return await message.answer("❗️ Tuman tanlashda xatolik!") # noqa
    await state.update_data(from_district=message.text)
    await state.set_state(ClientState.to_region)
    await message.answer("Qayerga bormoqchisiz?", reply_markup=region.as_markup(resize_keyboard=True))


@order_taxi_router.message(ClientState.to_region)
async def process_to_region(message: Message, state: FSMContext):
    if message.text not in region_list:
        return await message.answer("❗️Viloyat tanlashda xatolik yuz berdi, iltimos quyidagi viloyatlardan birini tanlang!") # noqa
    await state.update_data(to_region=message.text)
    await state.set_state(ClientState.to_district)
    await message.answer("❗️ Tumanni tanlang", reply_markup=make_district(message.text).as_markup(resize_keyboard=True))


@order_taxi_router.message(ClientState.to_district)
async def process_to_district(message: Message, state: FSMContext):
    region_name = (await state.get_data())['to_region']
    if message.text not in get_districts_by_region(region_name):
        return await message.answer("❗️ Tuman tanlashda xatolik!") # noqa
    await state.update_data(to_district=message.text)
    await state.set_state(ClientState.price)
    await message.answer("Naxrini kiriting: ", reply_markup=treaty.as_markup(resize_keyboard=True)) # noqa


@order_taxi_router.message(ClientState.price)
async def process_to_district(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(price=message.text)
    if data['type'] == 'Yetib borish':
        await state.set_state(ClientState.passenger_count)
        await message.answer("Necha kishi ketasizlar?", reply_markup=button_1234.as_markup(resize_keyboard=True)) # noqa
    else:
        await state.set_state(ClientState.additional_info)
        await message.answer("Qo'shimcha ma'lumot kiritishingiz mumkin:", reply_markup=skip.as_markup(resize_keyboard=True)) # noqa


@order_taxi_router.message(ClientState.passenger_count)
async def process_to_district(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(passenger_count=int(message.text))
        await state.set_state(ClientState.additional_info)
        return await message.answer("Qo'shimcha ma'lumot kiritishingiz mumkin:", reply_markup=skip.as_markup(resize_keyboard=True)) # noqa
    await message.answer('❗️ Faqat raqamlarda kiriting')


@order_taxi_router.message(ClientState.additional_info)
async def process_to_district(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_without_passenger_count = """
🛣 Taxi turi: {type}
🏘 Qayerdan: {from_region}, {from_district}
🚕 Qayerga: {to_region}, {to_district}
""".format(**data)
    msg = """
🛣 Taxi turi: {type}
🏘 Qayerdan: {from_region}, {from_district}
🚕 Qayerga: {to_region}, {to_district}
👤 Yo'lovchilar soni: {passenger_count} ta
""".format(**data)
    result = msg if data.get('passenger_count') else msg_without_passenger_count
    result += f"💰 Narxi: {data['price'] if data['price'].isdigit() else '🤝 Kelishuv'}\n"
    if message.text != "O'tkazib yuborish":
        await state.update_data(additional_info=message.text)
        result += f"ℹ️ Qo'shimcha ma'lumot: {message.text}"
    await message.answer(result, reply_markup=accept_or_not.as_markup(resize_keyboard=True))


