"use client";

import { useState } from "react";
import { useMutation } from "@apollo/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { CREATE_AD } from "@/lib/mutations/createAd"; // Путь до вашей мутации
import { useRouter } from "next/navigation";

export default function CreateAdPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState<number | string>("");
  const [images, setImages] = useState<string[]>([]);
  const [createAd, { loading, error }] = useMutation(CREATE_AD!);

  const router = useRouter();

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const uploadedImages = Array.from(e.target.files).map((file) =>
        URL.createObjectURL(file)
      );
      setImages(uploadedImages);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const { data } = await createAd({
        variables: {
          input: {
            title,
            description,
            price: parseInt(price as string),
            images,
          },
        },
      });

      // После успешного создания объявления, перенаправляем на страницу объявления
      router.push(`/ads/${data.createAd.id}`);
    } catch (err) {
      console.error("Ошибка создания объявления:", err);
    }
  };

  return (
    <div className="container mx-auto py-6 px-30">
      <h2 className="text-2xl mb-6">Создать объявление</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700"
          >
            Название
          </label>
          <Input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Введите название объявления"
          />
        </div>

        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700"
          >
            Описание
          </label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            placeholder="Введите описание"
          />
        </div>

        <div>
          <label
            htmlFor="price"
            className="block text-sm font-medium text-gray-700"
          >
            Цена
          </label>
          <Input
            id="price"
            type="number"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
            placeholder="Введите цену"
          />
        </div>

        <div>
          <label
            htmlFor="images"
            className="block text-sm font-medium text-gray-700"
          >
            Загрузить изображения
          </label>
          <input type="text" onChange={handleImageUpload} className="mt-2" />
          <div className="mt-2">
            {images.length > 0 && (
              <div className="flex space-x-4">
                {images.map((image, index) => (
                  <img
                    key={index}
                    src={image}
                    alt={`uploaded-${index}`}
                    className="w-24 h-24 object-cover rounded-lg"
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <Button type="submit" disabled={loading}>
            {loading ? "Загрузка..." : "Создать объявление"}
          </Button>
        </div>

        {error && (
          <div className="text-red-500">
            Ошибка при создании объявления: {error.message}
          </div>
        )}
      </form>
    </div>
  );
}
