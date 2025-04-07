"use client";

import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { Button } from "@/components/ui/Button";
import { Select, SelectTrigger, SelectContent, SelectItem } from "@/components/ui/Select";
import { useState } from "react";

const ExportChart = ({ exportRef }: { exportRef: React.RefObject<HTMLDivElement | null> }) => {
    const [exportFormat, setExportFormat] = useState("png");

    const handleExport = async () => {
        if (!exportRef?.current) return;

        const canvas = await html2canvas(exportRef?.current, { scale: 2 });

        if (exportFormat === "pdf") {
            const pdf = new jsPDF("landscape", "mm", "a4");
            const imgData = canvas.toDataURL("image/png");
            pdf.addImage(imgData, "PNG", 10, 10, 280, 190);
            pdf.save("chart.pdf");
        } else {
            const link = document.createElement("a");
            link.href = canvas.toDataURL(`image/${exportFormat}`);
            link.download = `chart.${exportFormat}`;
            link.click();
        }
    };

    return (
        <div className="flex items-center space-x-4">
            <Select value={exportFormat} onValueChange={setExportFormat}>
                <SelectTrigger>{exportFormat.toUpperCase()}</SelectTrigger>
                <SelectContent>
                    <SelectItem value="png">PNG</SelectItem>
                    <SelectItem value="jpeg">JPEG</SelectItem>
                    <SelectItem value="pdf">PDF</SelectItem>
                </SelectContent>
            </Select>

            <Button onClick={handleExport}>📥 Скачать {exportFormat.toUpperCase()}</Button>
        </div>
    );
};

export default ExportChart;
