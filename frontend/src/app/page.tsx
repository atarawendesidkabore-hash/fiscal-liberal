import { redirect } from "next/navigation";
import { marketingHref } from "@/lib/marketing-url";

export default function Home() {
  redirect(marketingHref("/"));
}
