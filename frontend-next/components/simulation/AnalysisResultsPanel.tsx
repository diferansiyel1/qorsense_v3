
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowUp, ArrowDown, Activity, TrendingUp, Zap } from "lucide-react";

interface AnalysisResult {
    healthScore: number;
    bias: number;
    slope: number;
    dfa: number;
    hysteresisArea: number;
    diagnosis: string;
}

interface AnalysisResultsPanelProps {
    result: AnalysisResult | null;
    previousResult: AnalysisResult | null;
}

export function AnalysisResultsPanel({ result, previousResult }: AnalysisResultsPanelProps) {
    if (!result) {
        return (
            <div className="h-full flex items-center justify-center text-muted-foreground bg-card/20 rounded-lg border border-dashed border-border/50">
                Run simulation to see results
            </div>
        );
    }

    const getDiff = (key: keyof AnalysisResult) => {
        if (!previousResult) return null;
        const diff = (result[key] as number) - (previousResult[key] as number);
        if (Math.abs(diff) < 0.001) return null;

        return (
            <span className={`text-xs ml-2 flex items-center ${diff > 0 ? "text-status-red" : "text-status-green"}`}>
                {diff > 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                {Math.abs(diff).toFixed(2)}
            </span>
        );
    };

    return (
        <div className="h-full flex flex-row gap-4">
            {/* Score Card - Vertical in Left Slot */}
            <Card className="w-1/4 bg-card/50 border-primary/20 flex flex-col justify-center">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Health Score</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-baseline justify-between">
                        <div className="text-4xl font-bold text-primary">
                            {result.healthScore.toFixed(0)}
                            <span className="text-sm font-normal text-muted-foreground ml-1">/ 100</span>
                        </div>
                    </div>
                    <div className="mt-2 text-sm font-mono text-cyan-500">
                        {result.diagnosis}
                    </div>
                </CardContent>
            </Card>

            {/* Metrics Matrix - Horizontal Grid */}
            <div className="w-3/4 grid grid-cols-4 gap-4">
                <Card className="bg-card/30">
                    <CardHeader className="p-4 pb-2">
                        <CardTitle className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                            <TrendingUp className="w-3 h-3" /> Slope
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                        <div className="text-xl font-bold flex items-center">
                            {result.slope.toFixed(4)}
                            {getDiff('slope')}
                        </div>
                    </CardContent>
                </Card>

                <Card className="bg-card/30">
                    <CardHeader className="p-4 pb-2">
                        <CardTitle className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                            <Activity className="w-3 h-3" /> Bias
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                        <div className="text-xl font-bold flex items-center">
                            {result.bias.toFixed(2)}
                            {getDiff('bias')}
                        </div>
                    </CardContent>
                </Card>

                <Card className="bg-card/30">
                    <CardHeader className="p-4 pb-2">
                        <CardTitle className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                            <Zap className="w-3 h-3" /> DFA (Hurst)
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                        <div className="text-xl font-bold flex items-center">
                            {result.dfa.toFixed(2)}
                            {getDiff('dfa')}
                        </div>
                    </CardContent>
                </Card>

                <Card className="bg-card/30">
                    <CardHeader className="p-4 pb-2">
                        <CardTitle className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                            <Activity className="w-3 h-3" /> Hysteresis
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                        <div className="text-xl font-bold flex items-center">
                            {result.hysteresisArea.toFixed(2)}
                            {getDiff('hysteresisArea')}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
