const DEFAULT_MARKETING_URL = "http://localhost:3101";

function trimTrailingSlash(value: string) {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

export const MARKETING_URL = trimTrailingSlash(
  process.env.NEXT_PUBLIC_MARKETING_URL || DEFAULT_MARKETING_URL
);

export function marketingHref(path: string = "/") {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${MARKETING_URL}${normalizedPath}`;
}
