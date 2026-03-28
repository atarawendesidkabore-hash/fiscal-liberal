const DEFAULT_APP_URL = "http://localhost:3100";

function trimTrailingSlash(value: string) {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

export const APP_URL = trimTrailingSlash(
  process.env.NEXT_PUBLIC_APP_URL || DEFAULT_APP_URL
);

export function appHref(path: string = "/") {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${APP_URL}${normalizedPath}`;
}
