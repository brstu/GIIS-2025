import AdDetails from "@/components/AdDetails";

export default function Page({ params }: { params: { adid: string } }) {
  return <AdDetails adid={params.adid} />;
}
