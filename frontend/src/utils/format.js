import dayjs from "dayjs";

const currency = import.meta.env.VITE_CURRENCY ?? "USD";

export function formatMoney(value) {
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return value;
  }

  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(value) {
  return dayjs(value).format("MMM D, YYYY");
}

export function monthLabel(month, year) {
  return dayjs(`${year}-${month}-01`).format("MMM YYYY");
}

export function todayIso() {
  return dayjs().format("YYYY-MM-DD");
}
