import os
import tempfile
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageTemplate, Frame
from reportlab.pdfgen import canvas
import plotly.graph_objects as go

# --- Chart Generation Helper ---
def generate_chart_image(data: list) -> str:
    """Generates a static image of the data trend using Plotly."""
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=data, mode='lines', name='Sensor Data', line=dict(color='#8b5cf6', width=2)))
        fig.update_layout(
            title="Sensor Data Trend",
            xaxis_title="Time Step",
            yaxis_title="Value",
            width=800,
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.5)'
        )
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.write_image(temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"Chart generation failed: {e}")
        return None

# --- Report Generator Class ---
class QorSenseReportGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=20*mm, leftMargin=20*mm,
            topMargin=40*mm, bottomMargin=20*mm
        )
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=20,
            alignment=1 # Center
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#8b5cf6'), # Primary Purple
            spaceBefore=15,
            spaceAfter=10,
            borderPadding=5,
            borderColor=colors.HexColor('#e5e7eb'),
            borderWidth=0,
            borderBottomWidth=1
        ))
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='WarningText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            spaceAfter=6
        ))

    def _header_footer(self, canvas, doc):
        # Save state
        canvas.saveState()
        
        # --- Header ---
        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 20*mm, 275*mm, width=40*mm, height=15*mm, preserveAspectRatio=True, mask='auto')
        else:
            canvas.setFont('Helvetica-Bold', 20)
            canvas.setFillColor(colors.HexColor('#8b5cf6'))
            canvas.drawString(20*mm, 280*mm, "QorSense")

        # Header Text
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor('#111827'))
        canvas.drawRightString(190*mm, 282*mm, "CERTIFICATE OF ANALYSIS")
        
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        canvas.drawRightString(190*mm, 277*mm, f"Date: {timestamp}")
        
        # Purple Line
        canvas.setStrokeColor(colors.HexColor('#8b5cf6'))
        canvas.setLineWidth(2)
        canvas.line(20*mm, 270*mm, 190*mm, 270*mm)
        
        # --- Footer ---
        canvas.setStrokeColor(colors.HexColor('#e5e7eb'))
        canvas.setLineWidth(1)
        canvas.line(20*mm, 20*mm, 190*mm, 20*mm)
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#9ca3af'))
        canvas.drawString(20*mm, 15*mm, "QorSense Technologies - Proprietary & Confidential")
        canvas.drawRightString(190*mm, 15*mm, f"Page {doc.page}")
        
        canvas.restoreState()

    def create_health_gauge(self, score):
        # Determine color
        if score >= 85:
            color = colors.HexColor('#10b981') # Green
            status = "OPTIMAL"
        elif score >= 60:
            color = colors.HexColor('#f59e0b') # Yellow
            status = "WARNING"
        else:
            color = colors.HexColor('#ef4444') # Red
            status = "CRITICAL"
            
        # Create a simple table for the score
        data = [
            [Paragraph(f"{score:.1f} / 100", self.styles['ReportTitle'])],
            [Paragraph(status, ParagraphStyle('Status', parent=self.styles['Normal'], alignment=1, textColor=color, fontSize=12, fontName='Helvetica-Bold'))]
        ]
        t = Table(data, colWidths=[170*mm])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 2, color),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9fafb')),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]) # ReportLab 3.6+ supports rounded corners? If not, it ignores.
        ]))
        return t

    def create_metrics_table(self, metrics):
        # Define thresholds for highlighting (simplified logic, ideally passed from config)
        # We'll just highlight if it looks "bad" based on typical values or if flags exist
        
        header = ["Metric", "Value", "Unit", "Status"]
        data = [header]
        
        # Helper to check status
        def get_status_row(name, value, unit, is_critical=False):
            status = "Normal"
            text_color = colors.black
            
            # Simple hardcoded checks for demo visualization (real logic should come from AnalysisResult flags)
            if name == "Slope" and abs(value) > 0.05:
                status = "Drift"
                text_color = colors.red
            elif name == "SNR (dB)" and value < 15:
                status = "Noisy"
                text_color = colors.red
            elif name == "Hurst" and value > 0.8:
                status = "Persistent"
                text_color = colors.orange
            
            # Format value
            val_str = f"{value:.4f}"
            
            return [
                Paragraph(name, self.styles['NormalText']),
                Paragraph(val_str, self.styles['NormalText']),
                Paragraph(unit, self.styles['NormalText']),
                Paragraph(status, ParagraphStyle('CellStatus', parent=self.styles['NormalText'], textColor=text_color))
            ]

        data.append(get_status_row("Bias", metrics.get('bias', 0), "Offset"))
        data.append(get_status_row("Slope", metrics.get('slope', 0), "Unit/s"))
        data.append(get_status_row("Noise (Std)", metrics.get('noise_std', 0), "RMS"))
        data.append(get_status_row("SNR (dB)", metrics.get('snr_db', 0), "dB"))
        data.append(get_status_row("Hysteresis", metrics.get('hysteresis', 0), "%"))
        data.append(get_status_row("Hurst Exponent", metrics.get('hurst', 0.5), "0-1"))
        data.append(get_status_row("Hurst R²", metrics.get('hurst_r2', 0), "0-1"))

        t = Table(data, colWidths=[50*mm, 40*mm, 30*mm, 40*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#374151')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    def generate(self, metrics, diagnosis, health_score, chart_path=None):
        story = []
        
        # 1. Executive Summary (Health Score)
        story.append(Paragraph(f"Sensor ID: {metrics.get('sensor_id', 'Unknown')}", self.styles['SectionHeader']))
        story.append(Spacer(1, 5*mm))
        story.append(self.create_health_gauge(health_score))
        story.append(Spacer(1, 10*mm))
        
        # 2. Diagnosis
        story.append(Paragraph("AI Diagnosis & Analysis", self.styles['SectionHeader']))
        story.append(Paragraph(diagnosis, self.styles['NormalText']))
        
        if metrics.get('recommendation'):
            story.append(Spacer(1, 3*mm))
            story.append(Paragraph(f"<b>Recommendation:</b> {metrics.get('recommendation')}", self.styles['NormalText']))
            
        if metrics.get('flags'):
            story.append(Spacer(1, 3*mm))
            flags_str = ", ".join(metrics.get('flags'))
            story.append(Paragraph(f"<b>Active Flags:</b> {flags_str}", self.styles['WarningText']))
            
        story.append(Spacer(1, 10*mm))
        
        # 3. Technical Metrics
        story.append(Paragraph("Technical Metrics", self.styles['SectionHeader']))
        story.append(self.create_metrics_table(metrics))
        
        # 4. Hurst Exponent Info
        story.append(Spacer(1, 5*mm))
        hurst_info = """
        <b>About Hurst Exponent (DFA):</b> The Hurst exponent (H) measures the long-term memory of a time series. 
        H=0.5 indicates a random walk (uncorrelated). H>0.5 indicates a persistent trend (drift). H<0.5 indicates anti-persistence (oscillation).
        """
        story.append(Paragraph(hurst_info, ParagraphStyle('Info', parent=self.styles['NormalText'], fontSize=8, textColor=colors.gray)))
        
        story.append(Spacer(1, 10*mm))
        
        # 5. Charts
        if chart_path and os.path.exists(chart_path):
            story.append(Paragraph("Data Visualization", self.styles['SectionHeader']))
            img = Image(chart_path, width=170*mm, height=70*mm)
            story.append(img)
            
        # Build
        self.doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)

# --- Main Interface ---
def create_pdf(metrics: dict, diagnosis: str, health_score: float, chart_image_path: str = None) -> str:
    """
    Wrapper function to maintain compatibility with existing code.
    Generates the new ReportLab PDF.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    generator = QorSenseReportGenerator(temp_file.name)
    generator.generate(metrics, diagnosis, health_score, chart_image_path)
    return temp_file.name
