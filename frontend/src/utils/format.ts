import dayjs from "dayjs";

const currency = import.meta.env.VITE_CURRENCY ?? "USD";

export function formatMoney(value: string | number): string {
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return String(value);
  }

  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(value: string): string {
  return dayjs(value).format("MMM D, YYYY");
}

export function monthLabel(month: number, year: number | string): string {
  return dayjs(`${year}-${month}-01`).format("MMM YYYY");
}

export function todayIso(): string {
  return dayjs().format("YYYY-MM-DD");
}
