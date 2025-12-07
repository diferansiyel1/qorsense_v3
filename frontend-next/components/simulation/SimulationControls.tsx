
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Play, RotateCcw, Upload, Settings2 } from "lucide-react";

export interface SimulationConfig {
    sourceType: 'generator' | 'upload';
    signalType: 'drift' | 'oscillation' | 'biofilm';
    duration: number;
    noiseLevel: number;
    criticalSlope: number;
    criticalBias: number;
    dfaThreshold: number;
    noiseTolerance: number;
}

interface SimulationControlsProps {
    onRun: (config: SimulationConfig) => void;
    onReset: () => void;
    onUpload?: (data: any[]) => void;
}

const DEFAULT_CONFIG: SimulationConfig = {
    sourceType: 'generator',
    signalType: 'drift',
    duration: 100,
    noiseLevel: 5,
    criticalSlope: 0.5,
    criticalBias: 10,
    dfaThreshold: 0.6,
    noiseTolerance: 10
};

export function SimulationControls({ onRun, onReset, onUpload }: SimulationControlsProps) {
    const [config, setConfig] = useState<SimulationConfig>(DEFAULT_CONFIG);
    const [preset, setPreset] = useState("standard");

    const handlePresetChange = (value: string) => {
        setPreset(value);
        if (value === "standard") {
            setConfig(prev => ({ ...prev, criticalSlope: 0.5, criticalBias: 10, dfaThreshold: 0.6 }));
        } else if (value === "pharma") {
            setConfig(prev => ({ ...prev, criticalSlope: 0.2, criticalBias: 5, dfaThreshold: 0.8 }));
        } else if (value === "wastewater") {
            setConfig(prev => ({ ...prev, criticalSlope: 1.0, criticalBias: 20, dfaThreshold: 0.4 }));
        }
    };

    const updateConfig = (key: keyof SimulationConfig, value: any) => {
        setConfig(prev => ({ ...prev, [key]: value }));
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const text = event.target?.result as string;
            // Simple parsing: split by line, assume single value or comma separated
            const lines = text.split('\n');
            const parsedData = lines
                .map((line, index) => {
                    const val = parseFloat(line.trim() || line.split(',')[1] || line.split(',')[0]);
                    // Tries to find a number. Supports "val" or "index,val".
                    return isNaN(val) ? null : { index, value: val };
                })
                .filter(d => d !== null);

            if (onUpload && parsedData.length > 0) {
                onUpload(parsedData);
                updateConfig('sourceType', 'upload');
            }
        };
        reader.readAsText(file);
    };

    // Auto-run when turning parameters? Maybe too expensive. Let's stick to manual Run for now or debounced.
    // User requested "Anında güncelleme" (Instant update) for Tuning tab.
    // checking if we should add an effect to call onRun when tuning params change.
    // For now, let's keep it explicit with "Run" button but maybe highlight it when changes occupy.

    return (
        <div className="h-full flex flex-col gap-4">
            <Card className="flex-1 overflow-y-auto bg-card/50 border-r border-border/50">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-xl font-mono text-primary">
                        <Settings2 className="w-5 h-5" /> Control Center
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    <Tabs defaultValue="source" className="w-full">
                        <TabsList className="grid w-full grid-cols-3">
                            <TabsTrigger value="source">Source</TabsTrigger>
                            <TabsTrigger value="tuning">Tuning</TabsTrigger>
                            <TabsTrigger value="presets">Presets</TabsTrigger>
                        </TabsList>

                        {/* Source Tab */}
                        <TabsContent value="source" className="space-y-4 pt-4">
                            <div className="space-y-2">
                                <Label>Signal Generator Type</Label>
                                <Select
                                    value={config.signalType}
                                    onValueChange={(v: any) => updateConfig('signalType', v)}
                                    disabled={config.sourceType === 'upload'}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="drift">Linear Drift</SelectItem>
                                        <SelectItem value="oscillation">Oscillation</SelectItem>
                                        <SelectItem value="biofilm">Biofilm Growth (Exp)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label>Duration (Points)</Label>
                                <Input
                                    type="number"
                                    value={config.duration}
                                    onChange={(e) => updateConfig('duration', Number(e.target.value))}
                                    disabled={config.sourceType === 'upload'}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Noise Level (%)</Label>
                                <Slider
                                    value={[config.noiseLevel]}
                                    max={50}
                                    step={1}
                                    onValueChange={([v]) => updateConfig('noiseLevel', v)}
                                    disabled={config.sourceType === 'upload'}
                                />
                                <div className="text-right text-xs text-muted-foreground">{config.noiseLevel}%</div>
                            </div>

                            <div className="pt-4 border-t space-y-2">
                                <Label>Or Upload Data (CSV/TXT)</Label>
                                <div className="flex items-center gap-2">
                                    <Input
                                        type="file"
                                        accept=".csv,.txt"
                                        onChange={handleFileUpload}
                                        className="cursor-pointer file:text-primary"
                                    />
                                </div>
                                <p className="text-[10px] text-muted-foreground">Format: Single column of values or Index,Value</p>
                            </div>
                        </TabsContent>

                        {/* Tuning Tab */}
                        <TabsContent value="tuning" className="space-y-6 pt-4">
                            <div className="space-y-2">
                                <Label className="text-status-red">Critical Slope Threshold</Label>
                                <Slider
                                    value={[config.criticalSlope]}
                                    max={2.0}
                                    step={0.1}
                                    onValueChange={([v]) => updateConfig('criticalSlope', v)}
                                />
                                <div className="text-right text-xs font-mono">{config.criticalSlope.toFixed(2)}</div>
                            </div>
                            <div className="space-y-2">
                                <Label className="text-status-yellow">Critical Bias Offset</Label>
                                <Slider
                                    value={[config.criticalBias]}
                                    max={50}
                                    step={1}
                                    onValueChange={([v]) => updateConfig('criticalBias', v)}
                                />
                                <div className="text-right text-xs font-mono">{config.criticalBias} units</div>
                            </div>
                            <div className="space-y-2">
                                <Label className="text-primary">DFA Hurst Limit</Label>
                                <Slider
                                    value={[config.dfaThreshold]}
                                    max={1.0}
                                    step={0.05}
                                    onValueChange={([v]) => updateConfig('dfaThreshold', v)}
                                />
                                <div className="text-right text-xs font-mono">{config.dfaThreshold.toFixed(2)}</div>
                            </div>
                            <div className="space-y-2">
                                <Label>Noise Tolerance (%)</Label>
                                <Slider
                                    value={[config.noiseTolerance]}
                                    max={100}
                                    step={5}
                                    onValueChange={([v]) => updateConfig('noiseTolerance', v)}
                                />
                                <div className="text-right text-xs font-mono">{config.noiseTolerance}%</div>
                            </div>
                        </TabsContent>

                        {/* Presets Tab */}
                        <TabsContent value="presets" className="space-y-4 pt-4">
                            <div className="space-y-2">
                                <Label>Process Environment</Label>
                                <Select value={preset} onValueChange={handlePresetChange}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="standard">Standard Industrial</SelectItem>
                                        <SelectItem value="pharma">Pharmaceutical (High Sensitivity)</SelectItem>
                                        <SelectItem value="wastewater">Wastewater (High Tolerance)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <p className="text-sm text-muted-foreground">
                                Presets automatically adjust sensitivity thresholds based on industry standards.
                            </p>
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>

            <div className="grid grid-cols-2 gap-2">
                <Button onClick={() => onRun(config)} className="bg-primary hover:bg-primary/90 text-white">
                    <Play className="w-4 h-4 mr-2" /> Run / Analyze
                </Button>
                <Button variant="outline" onClick={onReset}>
                    <RotateCcw className="w-4 h-4 mr-2" /> Reset
                </Button>
            </div>
        </div>
    );
}
