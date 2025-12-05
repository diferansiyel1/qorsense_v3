"use client";

import { useState } from 'react';
import { SmartSensorCard } from "@/components/SmartSensorCard";
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer, YAxis, CartesianGrid } from 'recharts';
import { Activity, ShieldAlert, Plus, Microscope } from 'lucide-react';
import { Button } from "@/components/ui/button";

const mockSensorsInitially = [
    { id: '1', name: 'Bioreactor pH Probe 01', healthScore: 98, status: 'Normal' as const },
    { id: '2', name: 'DO Probe @ Mix Tank', healthScore: 72, status: 'Warning' as const, problem: 'Membrane Fouling' },
    { id: '3', name: 'Main Line Flowmeter', healthScore: 45, status: 'Critical' as const, problem: 'Signal Noise' },
    { id: '4', name: 'Feed Pressure TX-101', healthScore: 92, status: 'Normal' as const },
];

const deviationData = [
    { time: '00:00', value: 0.12 },
    { time: '04:00', value: 0.15 },
    { time: '08:00', value: 0.28 },
    { time: '12:00', value: 0.45 },
    { time: '16:00', value: 0.42 },
    { time: '20:00', value: 0.38 },
    { time: '24:00', value: 0.35 },
];

export default function Dashboard() {
    const [sensors, setSensors] = useState(mockSensorsInitially);
    const [isAddProbeModalOpen, setIsAddProbeModalOpen] = useState(false);

    // Form State
    const [newProbeName, setNewProbeName] = useState('');
    const [newProbeType, setNewProbeType] = useState('pH Probe');

    const handleAddProbe = () => {
        const newId = (sensors.length + 1).toString();
        const newSensor = {
            id: newId,
            name: newProbeName || `${newProbeType} ${newId} `,
            healthScore: 100,
            status: 'Normal' as const
        };
        setSensors([...sensors, newSensor]);
        setIsAddProbeModalOpen(false);
        setNewProbeName('');
    };

    const criticalCount = sensors.filter(s => s.status === 'Critical').length;
    const warningCount = sensors.filter(s => s.status === 'Warning').length;

    return (
        <div className="min-h-screen bg-background p-6 md:p-8">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
                            <Microscope className="w-8 h-8 text-primary" />
                            Sensor Monitoring
                        </h1>
                        <p className="text-muted-foreground mt-1">Real-time analysis for pH, DO, Flow & Pressure instrumentation.</p>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Global Status Pill */}
                        <div className="hidden md:flex items-center gap-3 bg-card border border-border px-4 py-2 rounded-full shadow-sm">
                            <div className={`w - 3 h - 3 rounded - full ${criticalCount > 0 ? 'bg-status-red animate-pulse' : 'bg-status-green'} `}></div>
                            <span className="font-medium text-sm text-foreground">
                                {criticalCount > 0 ? "System Attention Required" : "All Systems Nominal"}
                            </span>
                        </div>

                        <Button
                            className="bg-primary hover:bg-primary-end text-white"
                            onClick={() => setIsAddProbeModalOpen(true)}
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Probe
                        </Button>
                    </div>
                </div>

                {/* KPI Overview */}
                {(criticalCount > 0 || warningCount > 0) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {criticalCount > 0 && (
                            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center gap-4">
                                <ShieldAlert className="w-8 h-8 text-status-red" />
                                <div>
                                    <h4 className="font-semibold text-status-red">Calibration Required</h4>
                                    <p className="text-sm text-muted-foreground">{criticalCount} probes showing significant drift or failure.</p>
                                </div>
                            </div>
                        )}
                        {warningCount > 0 && (
                            <div className="bg-status-yellow/10 border border-status-yellow/20 rounded-lg p-4 flex items-center gap-4">
                                <Activity className="w-8 h-8 text-status-yellow" />
                                <div>
                                    <h4 className="font-semibold text-status-yellow">Maintenance Warning</h4>
                                    <p className="text-sm text-muted-foreground">{warningCount} probes nearing end of life or require cleaning.</p>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Sensor Grid */}
                <div>
                    <div className="flex justify-between items-end mb-4">
                        <h2 className="text-xl font-semibold text-foreground">Active Instrumentation</h2>
                        <span className="text-sm text-muted-foreground">Total: {sensors.length}</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {sensors.map((sensor) => (
                            <SmartSensorCard key={sensor.id} {...sensor} />
                        ))}
                    </div>
                </div>

                {/* Global Deviation Chart */}
                <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
                    <div className="mb-6">
                        <h3 className="text-lg font-semibold text-foreground">Signal Quality Drift</h3>
                        <p className="text-sm text-muted-foreground">Aggregate noise levels across all analog inputs.</p>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={deviationData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorDeviation" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#00ADB5" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#00ADB5" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#2D3748" />
                                <XAxis
                                    dataKey="time"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', color: '#fff' }}
                                    itemStyle={{ color: '#00ADB5' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#00ADB5"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorDeviation)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Add Probe Modal Overlay */}
            {isAddProbeModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-card w-full max-w-md rounded-xl border border-border shadow-2xl p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-white">Add New Probe</h3>
                            <button onClick={() => setIsAddProbeModalOpen(false)} className="text-muted-foreground hover:text-white">✕</button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="text-sm font-medium text-muted-foreground block mb-2">Probe Name / Tag</label>
                                <input
                                    type="text"
                                    placeholder="e.g. Tank B pH Sensor"
                                    className="w-full bg-secondary border-border rounded-md px-3 py-2 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                                    value={newProbeName}
                                    onChange={(e) => setNewProbeName(e.target.value)}
                                />
                            </div>

                            <div>
                                <label className="text-sm font-medium text-muted-foreground block mb-2">Probe Type</label>
                                <select
                                    className="w-full bg-secondary border-border rounded-md px-3 py-2 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                                    value={newProbeType}
                                    onChange={(e) => setNewProbeType(e.target.value)}
                                >
                                    <option value="pH Probe">pH Sensor</option>
                                    <option value="DO Probe">Dissolved Oxygen (DO)</option>
                                    <option value="Conductivity">Conductivity Sensor</option>
                                    <option value="Pressure TX">Pressure Transmitter</option>
                                    <option value="Flowmeter">Flowmeter</option>
                                </select>
                            </div>

                            <div className="flex gap-3 mt-8 pt-4 border-t border-border">
                                <Button className="flex-1 bg-primary hover:bg-primary-end text-white" onClick={handleAddProbe}>
                                    Initialize Probe
                                </Button>
                                <Button variant="outline" className="flex-1" onClick={() => setIsAddProbeModalOpen(false)}>
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
