import { HomeClient } from "@/components/HomeClient";
import apis from "@/data/apis.json";
import { ApiRecord } from "@/lib/types";

export const metadata = {
  title: "Media Generation API Explorer",
  description: "Filterable catalog of media generation APIs with pricing, features, and examples"
};

export default function Page() {
  return <HomeClient apis={apis as ApiRecord[]} />;
}

