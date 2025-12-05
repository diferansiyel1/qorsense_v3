"use client";

import { useState, use } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    ScatterChart, Scatter, ReferenceLine
} from 'recharts';
import {
    Activity, ArrowLeft, AlertTriangle, Calendar, FileText,
    CheckCircle, Zap, Settings, TrendingUp, Droplets
} from 'lucide-react';
import Link from 'next/link';

// Mock Data Generators
const generateSignalData = () =>
    Array.from({ length: 100 }, (_, i) => ({
        time: i,
        raw: Math.sin(i * 0.2) + Math.random() * 0.5,
        filtered: Math.sin(i * 0.2)
    }));

const generateTrendData = () =>
    Array.from({ length: 30 }, (_, i) => ({
        day: i + 1,
        value: 0.5 + (i * 0.02) + (Math.random() * 0.1)
    }));

const dataSignal = generateSignalData();
const dataTrend = generateTrendData();

export default function SensorDetailPage(props: { params: Promise<{ id: string }> }) {
    // Unwrap params using React.use()
    const params = use(props.params);
    const [activeTab, setActiveTab] = useState<'diagnosis' | 'signal' | 'expert'>('diagnosis');
    const [isReportModalOpen, setIsReportModalOpen] = useState(false);

    // Mock Sensor Info based on ID
    const sensorId = params.id;
    const isCritical = sensorId === '3';

    // Logic to simulate different types based on ID
    const getSensorType = (id: string) => {
        if (id === '1') return { name: 'Bioreactor pH Probe 01', type: 'pH Sensor' };
        if (id === '2') return { name: 'DO Probe @ Mix Tank', type: 'Dissolved Oxygen' };
        if (id === '3') return { name: 'Main Line Flowmeter', type: 'Electromagnetic Flow' };
        return { name: `Pressure TX-${id}01`, type: 'Pressure Transmitter' };
    };

    const sensorInfo = getSensorType(sensorId);

    // Status Logic
    const rulDays = isCritical ? 3 : 14;
    const healthScore = isCritical ? 45 : 72;
    const statusColor = isCritical ? 'text-status-red' : 'text-status-yellow';
    const statusBg = isCritical ? 'bg-status-red/10 border-status-red/20' : 'bg-status-yellow/10 border-status-yellow/20';

    return (
        <div className="min-h-screen bg-background pb-20">
            {/* Top Navigation */}
            <div className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center text-muted-foreground hover:text-foreground transition-colors">
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Dashboard
                    </Link>
                    <div className="flex items-center gap-4">
                        <Button
                            variant="outline"
                            className="text-status-green border-status-green/50 hover:bg-status-green/10"
                            onClick={() => setIsReportModalOpen(true)}
                        >
                            <FileText className="w-4 h-4 mr-2" />
                            Generate Calibration Report
                        </Button>
                        <Button
                            className="bg-primary hover:bg-primary-end text-white"
                            onClick={() => setIsReportModalOpen(true)}
                        >
                            <Calendar className="w-4 h-4 mr-2" />
                            Schedule Replacement
                        </Button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">

                {/* Header Section: The "Doctor's Chart" */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="md:col-span-2 space-y-2">
                        <div className="flex items-center gap-3">
                            <Badge variant="outline" className="text-muted-foreground border-muted-foreground">TAG: {sensorId}-A2</Badge>
                            <span className="text-sm font-medium text-muted-foreground">{sensorInfo.type} • Process Line 1</span>
                        </div>
                        <h1 className="text-4xl font-bold text-foreground">{sensorInfo.name}</h1>
                        <p className="text-lg text-muted-foreground max-w-2xl">
                            Installed: 2024-01-15. Last Calibrated: 2 weeks ago.
                        </p>
                    </div>

                    {/* RUL Counter */}
                    <Card className={`text-center flex flex-col justify-center py-6 border-2 ${statusBg}`}>
                        <div className="text-sm uppercase tracking-widest text-muted-foreground font-semibold mb-1">Estimated Drift Limit (RUL)</div>
                        <div className={`text-6xl font-black ${statusColor} tracking-tighter`}>
                            {rulDays} <span className="text-xl font-normal text-muted-foreground">Days</span>
                        </div>
                        <div className="mt-2 text-sm text-foreground/80 font-medium">
                            {isCritical ? "⚠️ Calibration/Replacement Required" : "Signal Drift Detected"}
                        </div>
                    </Card>
                </div>

                {/* Main Content Areas */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

                    {/* Sidebar / Vitals */}
                    <div className="space-y-4">
                        <Card>
                            <CardHeader className="uppercase text-xs font-bold text-muted-foreground tracking-wider pb-2">Sensor Health</CardHeader>
                            <CardContent className="space-y-6">
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-muted-foreground">Overall Score</span>
                                        <span className={`font-bold ${statusColor}`}>{healthScore}%</span>
                                    </div>
                                    <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                                        <div className={`h-full ${isCritical ? 'bg-status-red' : 'bg-status-yellow'}`} style={{ width: `${healthScore}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-muted-foreground">Signal Noise (SNR)</span>
                                        <span className="font-bold text-foreground">12 dB</span>
                                    </div>
                                    <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                                        <div className="h-full bg-status-yellow" style={{ width: '65%' }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-muted-foreground">Response Time</span>
                                        <span className="font-bold text-foreground">1.8s</span>
                                    </div>
                                    <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                                        <div className="h-full bg-status-green" style={{ width: '90%' }}></div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-primary/5 border-primary/20">
                            <CardContent className="p-4 flex items-start gap-3">
                                <Zap className="w-5 h-5 text-primary mt-1" />
                                <div>
                                    <h4 className="font-bold text-primary text-sm">AI Diagnosis</h4>
                                    <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
                                        Analysis indicates <span className="text-foreground font-semibold">membrane fouling</span> or electrode aging. Impedance shift detected in high-frequency spectrum.
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Tabbed Analysis Area */}
                    <div className="lg:col-span-3">
                        {/* Custom Tabs */}
                        <div className="flex border-b border-border mb-6">
                            <button
                                onClick={() => setActiveTab('diagnosis')}
                                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'diagnosis' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                            >
                                Diagnosis
                            </button>
                            <button
                                onClick={() => setActiveTab('signal')}
                                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'signal' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                            >
                                Raw Signal
                            </button>
                            <button
                                onClick={() => setActiveTab('expert')}
                                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'expert' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                            >
                                Expert Analysis
                            </button>
                        </div>

                        {/* Tab Content */}
                        <div className="bg-card border border-border rounded-xl p-6 min-h-[400px]">

                            {activeTab === 'diagnosis' && (
                                <div className="space-y-6">
                                    <div className="flex justify-between items-center">
                                        <h3 className="text-lg font-semibold flex items-center gap-2">
                                            <TrendingUp className="w-5 h-5 text-status-yellow" />
                                            Signal Stability / Drift
                                        </h3>
                                        <Badge variant="outline" className="border-status-yellow text-status-yellow bg-status-yellow/5">Drift Warning</Badge>
                                    </div>
                                    <div className="h-[300px] w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={dataTrend}>
                                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#2D3748" />
                                                <XAxis dataKey="day" stroke="#94a3b8" tickLine={false} axisLine={false} />
                                                <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                                                />
                                                <ReferenceLine y={0.8} stroke="#E53E3E" strokeDasharray="3 3" label={{ value: 'Max Tolerance', fill: '#00ADB', fontSize: 12 }} />
                                                <Line type="monotone" dataKey="value" stroke="#00ADB5" strokeWidth={3} dot={{ r: 4, fill: '#0f172a', strokeWidth: 2 }} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                    <div className="p-4 bg-muted/50 rounded-lg border border-border text-sm">
                                        <p>The signal variance has increased by <strong>15%</strong>. This pattern is characteristic of <strong>drying electrolyte</strong> or <strong>coating on the sensor tip</strong>.</p>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'signal' && (
                                <div className="space-y-6">
                                    <h3 className="text-lg font-semibold flex items-center gap-2">
                                        <Droplets className="w-5 h-5 text-primary" />
                                        Raw Millivolt (mV) Input
                                    </h3>
                                    <div className="h-[300px] w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={dataSignal}>
                                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#2D3748" />
                                                <XAxis dataKey="time" stroke="#94a3b8" tickLine={false} axisLine={false} />
                                                <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                                                />
                                                <Line type="monotone" dataKey="raw" stroke="#4A5568" strokeWidth={1} dot={false} name="Raw mV" />
                                                <Line type="monotone" dataKey="filtered" stroke="#00ADB5" strokeWidth={2} dot={false} name="Filtered" />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'expert' && (
                                <div className="space-y-6">
                                    <h3 className="text-lg font-semibold flex items-center gap-2">
                                        <Settings className="w-5 h-5 text-primary" />
                                        Electrochemical Impedance Analysis
                                    </h3>
                                    <div className="h-[320px] w-full flex items-center justify-center border border-dashed border-border rounded-lg bg-muted/20">
                                        <p className="text-muted-foreground">Nyquist Plot Placeholder</p>
                                        {/* Placeholder for complex Scatter Chart */}
                                    </div>
                                </div>
                            )}

                        </div>
                    </div>
                </div>

            </div>

            {/* Modal / Report Confirmation */}
            {isReportModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-card w-full max-w-md rounded-xl border border-border shadow-2xl p-6 animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-xl font-bold">Maintenance Validation</h3>
                            <button onClick={() => setIsReportModalOpen(false)} className="text-muted-foreground hover:text-foreground">✕</button>
                        </div>

                        <div className="space-y-4">
                            <div className="p-4 bg-status-green/10 border border-status-green/20 rounded-lg">
                                <h4 className="font-semibold text-status-green flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4" /> Impact Analysis
                                </h4>
                                <p className="text-sm mt-1 text-foreground">
                                    Replacing <strong>{sensorInfo.name}</strong> maintains process sterility compliance and prevents batch rejection (Est. Saved: $12,500).
                                </p>
                            </div>

                            <p className="text-sm text-muted-foreground">
                                A calibration certificate request has been generated. Proceed with scheduling?
                            </p>

                            <div className="flex gap-3 mt-6">
                                <Button className="w-full bg-primary hover:bg-primary-end" onClick={() => setIsReportModalOpen(false)}>Create Work Order</Button>
                                <Button variant="outline" className="w-full" onClick={() => setIsReportModalOpen(false)}>Cancel</Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
