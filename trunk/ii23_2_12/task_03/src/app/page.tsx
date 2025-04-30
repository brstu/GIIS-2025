"use client";

export const dynamic = "force-dynamic";

import { Ads } from "@/components/Ads";
import { Filters } from "@/components/Filters";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { FilterIcon } from "lucide-react";

export default function Home() {
  return (
    <div className="container mx-auto py-6 space-y-6 px-30">
      <Card>
        <CardHeader className="flex justify-center">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/login">Вход</Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link href="/register">Регистрация</Link>
          </Button>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Объявления</CardTitle>
          {/* Мобильная кнопка фильтра */}
          <div className="md:hidden">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="sm">
                  <FilterIcon className="w-4 h-4 mr-2" />
                  Фильтры
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-[280px]">
                <Filters />
              </SheetContent>
            </Sheet>
          </div>
        </CardHeader>
        <CardContent className="grid md:grid-cols-[240px_1fr] gap-6">
          {/* Desktop фильтры */}
          <div className="hidden md:block">
            <Filters />
          </div>
          <div>
            <Ads />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
