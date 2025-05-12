"use client";

import { useQuery, gql } from "@apollo/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Filters } from "@/components/Filters";
import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet";
import { FilterIcon } from "lucide-react";
import { GET_USER_PROFILE } from "@/lib/queries/get-user";

export default function UserProfile() {
  const { data, loading, error } = useQuery(GET_USER_PROFILE);

  // Ошибки и загрузка
  if (loading) return <div className="text-center py-10">Загрузка...</div>;
  if (error)
    return <div className="text-center py-10">Ошибка загрузки профиля</div>;

  if (!data?.me)
    return <div className="text-center py-10">Пользователь не найден</div>;

  const { me } = data;

  return (
    <div className="container mx-auto py-6 space-y-6 px-30">
      <Card>
        <CardHeader className="flex justify-between">
          <CardTitle>Личный кабинет</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div>Имя пользователя: {me.username}</div>
            <div>Email: {me.email}</div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Мои объявления</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-[440px_1fr] gap-6">
          <div>
            {me.ads.length > 0 ? (
              <div className="grid gap-6">
                {me.ads.map((ad: any) => (
                  <div key={ad.id} className="border p-4 rounded-md">
                    <h3 className="text-xl font-semibold">{ad.title}</h3>
                    <p>{ad.description}</p>
                    <div className="mt-4">
                      <img
                        src={ad.images?.[0] || "/placeholder.jpg"}
                        alt={ad.title}
                        className="w-full h-48 object-cover rounded-md"
                      />
                    </div>
                    <div className="mt-2 text-lg font-medium">{ad.price} ₽</div>
                  </div>
                ))}
              </div>
            ) : (
              <div>У вас нет объявлений.</div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
