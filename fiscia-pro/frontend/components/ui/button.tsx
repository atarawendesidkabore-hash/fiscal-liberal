import { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({ className = "", ...props }: Props) {
  return <button className={`rounded bg-fiscal-500 px-3 py-2 text-white ${className}`} {...props} />;
}

