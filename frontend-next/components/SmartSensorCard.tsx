import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUpRight, Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

// We might not have the shadcn ui components generated yet, so I'll use raw tailwind for now 
// to ensure it works without needing to run npx shadcn-ui@latest add ...
// If I had shell access to interactive commands I would, but safest is to build standard components.

interface SmartSensorCardProps {
    id: string;
    name: string;
    healthScore: number;
    status: 'Normal' | 'Warning' | 'Critical';
    problem?: string;
}

export function SmartSensorCard({ id, name, healthScore, status, problem }: SmartSensorCardProps) {
    const statusColor = {
        Normal: 'bg-status-green border-status-green text-status-green',
        Warning: 'bg-status-yellow border-status-yellow text-status-yellow',
        Critical: 'bg-status-red border-status-red text-status-red',
    };

    const statusBorder = {
        Normal: 'border-l-4 border-l-status-green',
        Warning: 'border-l-4 border-l-status-yellow',
        Critical: 'border-l-4 border-l-status-red',
    };

    const glow = {
        Normal: 'shadow-[0_0_10px_rgba(0,200,81,0.1)]',
        Warning: 'shadow-[0_0_15px_rgba(255,187,51,0.15)]',
        Critical: 'shadow-[0_0_20px_rgba(255,68,68,0.2)] animate-pulse-slow',
    }

    return (
        <Link href={`/sensor/${id}`} className="block group">
            <div className={cn(
                "relative bg-card rounded-lg border border-border/50 overflow-hidden transition-all duration-300 hover:translate-y-[-2px] hover:shadow-lg",
                statusBorder[status],
                glow[status]
            )}>
                <div className="p-5">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                                {name}
                            </h3>
                            <div className="flex items-center mt-1 space-x-2">
                                <span className={cn("w-2 h-2 rounded-full", statusColor[status].split(" ")[0])}></span>
                                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                    {status}
                                </span>
                            </div>
                        </div>
                        {status === 'Normal' ? (
                            <CheckCircle className="w-5 h-5 text-status-green opacity-80" />
                        ) : status === 'Warning' ? (
                            <AlertTriangle className="w-5 h-5 text-status-yellow opacity-80" />
                        ) : (
                            <Activity className="w-5 h-5 text-status-red opacity-80" />
                        )}
                    </div>

                    <div className="flex items-end justify-between">
                        <div>
                            <p className="text-xs text-muted-foreground mb-1">Health Score</p>
                            <div className="flex items-baseline space-x-1">
                                <span className={cn("text-4xl font-bold tracking-tighter",
                                    status === 'Critical' ? 'text-status-red' :
                                        status === 'Warning' ? 'text-status-yellow' : 'text-foreground'
                                )}>
                                    {healthScore}
                                </span>
                                <span className="text-sm text-muted-foreground">/100</span>
                            </div>
                        </div>

                        {problem && (
                            <div className="absolute bottom-4 right-4 max-w-[50%] text-right bg-background/50 backdrop-blur-sm px-2 py-1 rounded border border-border/50">
                                <p className="text-xs font-medium text-status-red flex items-center justify-end gap-1">
                                    <ArrowUpRight className="w-3 h-3" />
                                    {problem}
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Decorative Tech Lines */}
                <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-white/5 to-transparent pointer-events-none"></div>
            </div>
        </Link>
    );
}
