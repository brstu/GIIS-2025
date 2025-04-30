"use client";

import { useQuery, useSuspenseQuery } from "@apollo/client";
import { GET_AD } from "@/lib/queries/get-ad";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Image from "next/image";

type Ad = {
  id: string;
  title: string;
  description: string;
  price: number;
  images: string[];
};

type GetAdResponse = {
  ad: Ad;
};

export default function AdDetails({ adid }: { adid: string }) {
  const { data, error } = useSuspenseQuery<GetAdResponse>(GET_AD, {
    variables: { id: adid },
    skip: !adid,
  });

  function getSafeImageUrl(src: string | undefined): string {
    if (!src) return "/placeholder.jpg";
    if (
      src.startsWith("http://") ||
      src.startsWith("https://") ||
      src.startsWith("/")
    ) {
      return src;
    }
    return "/placeholder.jpg";
  }

  if (error) return <div>Ошибка загрузки</div>;
  if (!data?.ad) return <div>Товар не найден</div>;

  const ad = data.ad;
  const imageUrl = getSafeImageUrl(ad.images?.[0]);

  return (
    <Card className="max-w-4xl mx-auto mt-8 shadow-lg rounded-2xl">
      <CardHeader>
        <CardTitle className="text-2xl md:text-3xl font-semibold">
          {ad.title}
        </CardTitle>
        <div className="text-muted-foreground text-sm mt-1">
          Объявление #{ad.id}
        </div>
      </CardHeader>
      <CardContent className="grid md:grid-cols-2 gap-6">
        {imageUrl && (
          <div className="relative w-full aspect-square rounded-xl overflow-hidden">
            <img
              src={getSafeImageUrl(ad.images?.[0])}
              alt={ad.title}
              className="rounded-xl"
            />
          </div>
        )}
        <div className="flex flex-col justify-between">
          <div>
            <p className="text-lg font-medium mb-2">Описание</p>
            <p className="text-muted-foreground">{ad.description}</p>
            <div className="mt-4">
              <Badge className="text-base py-1 px-3">{ad.price} ₽</Badge>
            </div>
          </div>
          <div className="mt-6">
            <Button size="lg" className="w-full">
              Связаться с продавцом
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
