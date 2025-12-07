
"use client";

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, Brush, Area } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SimulationConfig } from "./SimulationControls";

interface InteractiveAnalysisChartProps {
    data: any[];
    config: SimulationConfig;
    onBrushChange: (startIndex: number, endIndex: number) => void;
}

export function InteractiveAnalysisChart({ data, config, onBrushChange }: InteractiveAnalysisChartProps) {

    // Custom Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-background/90 border border-border p-2 rounded shadow-md text-xs">
                    <p className="font-bold">Time: {label}</p>
                    {payload.map((p: any) => (
                        <p key={p.name} style={{ color: p.color }}>
                            {p.name}: {p.value.toFixed(2)}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <Card className="h-full flex flex-col bg-card/50">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-mono text-cyan-400">Signal Analysis Lab</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 min-h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis dataKey="index" stroke="#666" fontSize={10} />
                        <YAxis stroke="#666" fontSize={10} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />

                        {/* The Signal */}
                        <Line
                            type="monotone"
                            dataKey="value"
                            stroke="#00ADB5"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 6 }}
                            name="Sensor Signal"
                        />

                        {/* Reference Lines from Config */}
                        {/* Example: Showing Bias Limit approx. Assuming standard deviation is around 1 */}
                        {/* We visualize the limits relative to the data range or fixed? 
                            Let's set pure horizontal lines for clear visualization. */}

                        <ReferenceLine y={config.criticalBias} label="Bias Limit (+)" stroke="#ef4444" strokeDasharray="3 3" />
                        <ReferenceLine y={-config.criticalBias} label="Bias Limit (-)" stroke="#ef4444" strokeDasharray="3 3" area-label="Critical Zone" />

                        {/* Brush for Zooming/Slicing */}
                        <Brush
                            dataKey="index"
                            height={30}
                            stroke="#8884d8"
                            onChange={(e: any) => {
                                if (e && e.startIndex !== undefined && e.endIndex !== undefined) {
                                    onBrushChange(e.startIndex, e.endIndex);
                                }
                            }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
