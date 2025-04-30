"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useState } from "react";

export function Filters() {
  const [price, setPrice] = useState([5000]);

  return (
    <div className="space-y-6">
      <div>
        <Label htmlFor="search">Поиск</Label>
        <Input id="search" placeholder="Например, iPhone 14" />
      </div>

      <Separator />

      <div>
        <Label>Цена до: {price[0]} ₽</Label>
        <Slider
          defaultValue={price}
          max={200000}
          step={1000}
          onValueChange={setPrice}
        />
      </div>

      <Separator />

      <div className="flex justify-end">
        <Button variant="default" className="w-full">
          Применить фильтры
        </Button>
      </div>
    </div>
  );
}
