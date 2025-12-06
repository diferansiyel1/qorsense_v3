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
    status: 'Normal' | 'Warning' | 'Critical' | 'Unknown';
    problem?: string;
}

export function SmartSensorCard({ id, name, healthScore, status, problem }: SmartSensorCardProps) {
    const statusColor = {
        Normal: 'bg-status-green border-status-green text-status-green',
        Warning: 'bg-status-yellow border-status-yellow text-status-yellow',
        Critical: 'bg-status-red border-status-red text-status-red',
        Unknown: 'bg-muted-foreground border-muted-foreground text-muted-foreground',
    };

    const statusBorder = {
        Normal: 'border-l-4 border-l-status-green',
        Warning: 'border-l-4 border-l-status-yellow',
        Critical: 'border-l-4 border-l-status-red',
        Unknown: 'border-l-4 border-l-muted-foreground',
    };

    const glow = {
        Normal: 'shadow-[0_0_10px_rgba(0,200,81,0.1)]',
        Warning: 'shadow-[0_0_15px_rgba(255,187,51,0.15)]',
        Critical: 'shadow-[0_0_20px_rgba(255,68,68,0.2)] animate-pulse-slow',
        Unknown: 'shadow-none',
    }

    return (
        <Link href={`/sensor/${id}`} className="block group">
            <div className={cn(
                "relative bg-card rounded-lg border border-border/50 overflow-hidden transition-all duration-300 hover:translate-y-[-2px] hover:shadow-lg",
                statusBorder[status] || statusBorder.Unknown,
                glow[status] || glow.Unknown
            )}>
                <div className="p-4">
                    <div className="flex justify-between items-start mb-3">
                        <div>
                            <h3 className="text-base font-bold text-gray-100 group-hover:text-primary transition-colors">
                                {name}
                            </h3>
                            <div className="flex items-center space-x-2 mb-4">
                                <span className={cn("w-2 h-2 rounded-full",
                                    status === 'Normal' ? 'bg-status-green shadow-[0_0_8px_#00C851]' :
                                        status === 'Warning' ? 'bg-status-yellow shadow-[0_0_8px_#FFBB33]' :
                                            status === 'Critical' ? 'bg-status-red shadow-[0_0_8px_#FF4444]' : 'bg-muted-foreground'
                                )}></span>
                                <span className={cn("text-[10px] font-bold uppercase tracking-wider",
                                    status === 'Normal' ? 'text-status-green' :
                                        status === 'Warning' ? 'text-status-yellow' :
                                            status === 'Critical' ? 'text-status-red' : 'text-muted-foreground'
                                )}>
                                    {status}
                                </span>
                            </div>
                        </div>
                        <div className={cn("p-2 rounded-lg border backdrop-blur-sm",
                            status === 'Normal' ? 'bg-status-green/10 border-status-green/20' :
                                status === 'Warning' ? 'bg-status-yellow/10 border-status-yellow/20' :
                                    status === 'Critical' ? 'bg-status-red/10 border-status-red/20' :
                                        'bg-muted/10 border-muted'
                        )}>
                            {status === 'Normal' ? (
                                <CheckCircle className="w-4 h-4 text-status-green" />
                            ) : status === 'Warning' ? (
                                <AlertTriangle className="w-4 h-4 text-status-yellow" />
                            ) : status === 'Critical' ? (
                                <Activity className="w-4 h-4 text-status-red" />
                            ) : (
                                <Activity className="w-4 h-4 text-muted-foreground opacity-50" />
                            )}
                        </div>
                    </div>

                    <div className="flex items-end justify-between">
                        <div>
                            <p className="text-[10px] text-muted-foreground mb-1">Health Score</p>
                            <div className="flex items-baseline space-x-1">
                                <span className={cn("text-4xl font-bold tracking-tighter tabular-nums",
                                    status === 'Normal' ? 'text-status-green' :
                                        status === 'Warning' ? 'text-status-yellow' :
                                            status === 'Critical' ? 'text-status-red' : 'text-muted-foreground'
                                )}>
                                    {healthScore}
                                </span>
                                <span className="text-xs text-muted-foreground">/100</span>
                            </div>
                        </div>

                        {problem && (
                            <div className={cn("absolute bottom-3 right-3 px-2.5 py-1 rounded-md border backdrop-blur-md",
                                status === 'Critical' ? 'bg-status-red/10 border-status-red/30' :
                                    status === 'Warning' ? 'bg-status-yellow/10 border-status-yellow/30' :
                                        'bg-muted/10 border-muted'
                            )}>
                                <p className={cn("text-[10px] font-bold uppercase tracking-tight flex items-center justify-end gap-1.5",
                                    status === 'Critical' ? 'text-status-red' :
                                        status === 'Warning' ? 'text-status-yellow' : 'text-muted-foreground'
                                )}>
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
