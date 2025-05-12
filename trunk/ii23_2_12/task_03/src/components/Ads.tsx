"use client";

import { useQuery, gql } from "@apollo/client";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";

const GET_ADS = gql`
  query GetAds {
    ads {
      id
      title
      description
      price
      images
    }
  }
`;

export function Ads() {
  const { data, loading, error } = useQuery(GET_ADS);

  if (loading) {
    return (
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="space-y-4">
            <CardHeader>
              <Skeleton className="w-full h-48 rounded-lg" />
              <Skeleton className="h-4 w-2/3 mt-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-3 w-full mb-2" />
              <Skeleton className="h-3 w-3/4" />
            </CardContent>
            <CardFooter className="justify-between">
              <Skeleton className="h-6 w-16" />
              <Skeleton className="h-6 w-20" />
            </CardFooter>
          </Card>
        ))}
      </div>
    );
  }

  if (error) return <p className="text-red-500">Ошибка загрузки объявлений</p>;

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {data.ads.map((ad: any) => (
        <Card key={ad.id} className="flex flex-col justify-between">
          <CardHeader>
            <img
              src={ad.images[0] || "https://via.placeholder.com/400x250"}
              alt={ad.title}
              className="w-full h-48 object-cover rounded-lg"
            />
            <CardTitle className="mt-4 text-lg">{ad.title}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {ad.description}
          </CardContent>
          <CardFooter className="flex items-center justify-between">
            <Badge variant="secondary">{ad.price.toLocaleString()} ₽</Badge>
            <Button size="sm">
              <Link href={`/ads/${ad.id}`}>Подробнее</Link>
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
