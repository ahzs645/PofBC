export const currentDistrictId = (number) => `school-district-${Number(number)}`
const slug = (value) => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
// Numbers have been reused. A historical district's name is part of its stable identifier.
export const formerDistrictId = (record) => record.id ?? `former-school-district-${record.number}-${slug(record.name)}`
