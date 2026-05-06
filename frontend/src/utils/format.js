export function currency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(value ?? 0);
}

export function number(value, digits = 1) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: digits
  }).format(value ?? 0);
}

export function compactDate(value) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric"
  }).format(new Date(value));
}

export function shortMonth(value) {
  return value?.replace(" 20", " '") ?? "";
}
