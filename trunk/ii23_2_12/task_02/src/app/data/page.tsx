"use client";

import React, { useState, useEffect, useRef } from "react";
import { Upload } from "lucide-react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    BarChart,
    Bar,
    ScatterChart,
    Scatter,
} from "recharts";
import { Card, CardContent } from "@/components/ui/Card";
import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/Select";
import { Switch } from "@/components/ui/switch";
import { Table } from "antd";
import ExportChart from "@/components/ExportChart";
import { aggregateData, normalizeData } from "@/lib";
import { processFileData } from "@/lib/processFileData";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/Button";

const DataVisualizer: React.FC = () => {
    const exportRef = useRef<HTMLDivElement>(null);
    const [fileName, setFileName] = useState<string | null>(null);
    const [data, setData] = useState<any[]>([]);
    const [aggregatedData, setAggregatedData] = useState<any[]>([]);
    const [chartType, setChartType] = useState("Линейный график");
    const [selectedDataKey, setSelectedDataKey] = useState<string>("value");
    const [aggregationMethod, setAggregationMethod] = useState("Сумма");
    const [isNormalizationEnabled, setIsNormalizationEnabled] = useState(true);

    useEffect(() => {
        if (data.length) {
            let aggregated = aggregateData(data, selectedDataKey, aggregationMethod);
            if (isNormalizationEnabled) {
                aggregated = normalizeData(aggregated, selectedDataKey);
            }
            setAggregatedData(aggregated);
        }
    }, [selectedDataKey, aggregationMethod, data, isNormalizationEnabled]);

    const columns = data.length
        ? Object.keys(data[0]).map((key) => ({
              title: key,
              dataIndex: key,
              key: key,
          }))
        : [];

    return (
        <div className="p-6">
            {data.length > 0 && (
            <div>
                <div className="flex justify-between">
                    <h1 className="text-2xl font-bold">Визуализация данных</h1>
                    <Dialog>
                            <DialogTrigger asChild>
                                <Button variant="outline">Подсказки</Button>
                            </DialogTrigger>
                            <DialogContent className="sm:max-w-[425px]">
                                <DialogHeader>
                                    <DialogTitle>Подсказки</DialogTitle>
                                </DialogHeader>
                                <div className="text-[#444] text-md leading-[130%] px-4">
                                    <ol className="flex flex-col gap-3 list-decimal">
                                        <li>Загрузите файл в формате CSV или Excel</li>
                                        <li>Выберите необходимые фильтры для визуализации данных (график, № столбца, агригирование, нормализация)</li>
                                        <li>Экспортируйте график в нужном формате</li>
                                    </ol>
                                </div>
                            </DialogContent>
                    </Dialog>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                    <p>📄 Загружен файл: <strong>{fileName}</strong></p>
                    <p>📊 Данных в файле: <strong>{data.length}</strong></p>
                    <p>🧮 После агрегации: <strong>{aggregatedData.length}</strong></p>
                    <p>📏 После нормализации: <strong>{isNormalizationEnabled ? aggregatedData.length : 'нормализация отключена'}</strong></p>
                </div>
                <div className="flex justify-between items-center mt-4  ">
                        <CardContent className="flex flex-col items-center w-fit -px-3">
                            <input
                                type="file"
                                accept=".csv,.xlsx"
                                onChange={(e) =>
                                    e.target.files?.[0] && processFileData(setFileName, e.target.files[0], setData)
                                }
                                className="hidden"
                                id="file-upload"
                            />
                            <label
                                htmlFor="file-upload"
                                className="cursor-pointer flex items-center space-x-2 border p-2 rounded-lg shadow hover:bg-accent">
                                <Upload size={20} />
                                <span>Загрузить файл</span>
                            </label>
                        </CardContent>
                        <ExportChart exportRef={exportRef} />
                </div>
            </div>
            )}
            {data.length > 0 ? (
                <div className="flex justify-between gap-10 mt-4">
                    <div className="w-[50%]">
                        <div className="sticky top-5 my-4">
                            <div className="flex items-center space-x-4 mb-10">
                                <h2 className="text-md font-semibold">фильтры:</h2>
                                <Select value={chartType} onValueChange={setChartType}>
                                    <SelectTrigger>{chartType}</SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="Линейный график">
                                            Линейный график
                                        </SelectItem>
                                        <SelectItem value="Гистограмма">Гистограмма</SelectItem>
                                        <SelectItem value="Диаграмма рассеяния">
                                            Диаграмма рассеяния
                                        </SelectItem>
                                    </SelectContent>
                                </Select>

                                <Select value={selectedDataKey} onValueChange={setSelectedDataKey}>
                                    <SelectTrigger>{selectedDataKey}</SelectTrigger>
                                    <SelectContent>
                                        {Object.keys(data[0] || {}).map((key) => (
                                            <SelectItem key={key} value={key}>
                                                {key}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>

                                <Select
                                    value={aggregationMethod}
                                    onValueChange={setAggregationMethod}>
                                    <SelectTrigger>{aggregationMethod}</SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="Сумма">Сумма</SelectItem>
                                        <SelectItem value="Среднее">Среднее</SelectItem>
                                        <SelectItem value="Максимум">Максимум</SelectItem>
                                        <SelectItem value="Минимум">Минимум</SelectItem>
                                    </SelectContent>
                                </Select>

                                {/* Тогл для включения/выключения нормализации */}
                                <div className="flex items-center space-x-2">
                                    <span>Нормализация</span>
                                    <Switch
                                        checked={isNormalizationEnabled}
                                        onCheckedChange={setIsNormalizationEnabled}
                                    />
                                </div>
                            </div>

                            <div ref={exportRef}>
                                <ResponsiveContainer width="100%" height={400}>
                                    {chartType === "Линейный график" && (
                                        <LineChart data={aggregatedData}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="name" />
                                            <YAxis />
                                            <Tooltip />
                                            <Legend />
                                            <Line
                                                type="monotone"
                                                dataKey={selectedDataKey}
                                                stroke="#8884d8"
                                            />
                                        </LineChart>
                                    )}

                                    {chartType === "Гистограмма" && (
                                        <BarChart data={aggregatedData}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="name" />
                                            <YAxis />
                                            <Tooltip />
                                            <Legend />
                                            <Bar dataKey={selectedDataKey} fill="#82ca9d" />
                                        </BarChart>
                                    )}

                                    {chartType === "Диаграмма рассеяния" && (
                                        <ScatterChart>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="x" name="Месяц" type="category" />
                                            <YAxis dataKey="y" name="Значение" />
                                            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                                            <Legend />
                                            <Scatter
                                                name="Данные"
                                                data={aggregatedData.map((d) => ({
                                                    x: d.name,
                                                    y: d[selectedDataKey],
                                                }))}
                                                fill="#8884d8"
                                            />
                                        </ScatterChart>
                                    )}
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    <Card className="p-5 w-[50%]">
                        <h2>📋 Таблица данных</h2>
                        <Table
                            dataSource={data}
                            columns={columns}
                            rowKey="name"
                            pagination={{ pageSize: 30 }}
                        />
                    </Card>
                </div>
            ) : (
                <Card className="flex items-center justify-center  m-5 p-20">
                    <CardContent className="flex flex-col items-center w-fit">
                        <input
                            type="file"
                            accept=".csv,.xlsx"
                            onChange={(e) =>
                                e.target.files?.[0] && processFileData(setFileName, e.target.files[0], setData)
                            }
                            className="hidden"
                            id="file-upload"
                        />
                        <label
                            htmlFor="file-upload"
                            className="cursor-pointer flex items-center space-x-2 border p-2 rounded-lg shadow hover:bg-accent">
                            <Upload size={20} />
                            <span>Загрузить файл</span>
                        </label>
                    </CardContent>
                    <p>Загрузите файл в формате .xlsx, .csv</p>
                </Card>
            )}
        </div>
    );
};

export default DataVisualizer;
