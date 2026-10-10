#!/usr/bin/env python3
"""Typeset paper.md using ReportLab. No model results are generated here."""
from __future__ import annotations

from html import escape
import re
from pathlib import Path
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, KeepTogether

ROOT = Path(__file__).resolve().parents[1]


def fonts():
    locations = [Path('/System/Library/Fonts/Supplemental'), Path('/usr/share/fonts/truetype/dejavu')]
    for folder in locations:
        if (folder / 'Times New Roman.ttf').exists():
            names = ['Times New Roman.ttf', 'Times New Roman Bold.ttf', 'Times New Roman Italic.ttf', 'Times New Roman Bold Italic.ttf']
        elif (folder / 'DejaVuSerif.ttf').exists():
            names = ['DejaVuSerif.ttf', 'DejaVuSerif-Bold.ttf', 'DejaVuSerif-Italic.ttf', 'DejaVuSerif-BoldItalic.ttf']
        else:
            continue
        for face, name in zip(['Paper','Paper-Bold','Paper-Italic','Paper-BoldItalic'], names):
            pdfmetrics.registerFont(TTFont(face, str(folder / name)))
        pdfmetrics.registerFontFamily('Paper', normal='Paper', bold='Paper-Bold', italic='Paper-Italic', boldItalic='Paper-BoldItalic')
        return 'Paper'
    return 'Times-Roman'


def inline(text):
    text = escape(text.replace('–', '-').replace('—', '-').replace('’', "'"))
    text = re.sub(r'h_i\^([+-])', r'h<sub>i</sub><super>\1</super>', text)
    text = text.replace('n_v', 'n<sub>v</sub>')
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#175271">\1</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
    return text


def equation(text):
    text = escape(text)
    text = re.sub(r'h_i\^([+-])', r'h<sub>i</sub><super>\1</super>', text)
    text = text.replace('n_v', 'n<sub>v</sub>').replace('sum_i', '∑<sub>i</sub>')
    text = text.replace('||', '‖').replace('_2', '<sub>2</sub>')
    return text.replace('alpha', 'α').replace("h'", 'h′')


def main():
    face = fonts()
    styles = getSampleStyleSheet()
    body = ParagraphStyle('BodyPaper', fontName=face, fontSize=10.5, leading=14.1, spaceAfter=7, allowWidows=0, allowOrphans=0, textColor=colors.HexColor('#18232b'))
    title = ParagraphStyle('TitlePaper', parent=body, fontSize=22, leading=26, alignment=TA_CENTER, spaceAfter=18, fontName='Paper-Bold' if face=='Paper' else 'Times-Bold')
    h2 = ParagraphStyle('HeadingPaper', parent=body, fontSize=14, leading=18, spaceBefore=15, spaceAfter=8, keepWithNext=True, fontName='Paper-Bold' if face=='Paper' else 'Times-Bold')
    h3 = ParagraphStyle('SubheadingPaper', parent=h2, fontSize=11.5, leading=15, spaceBefore=10)
    cell = ParagraphStyle('CellPaper', parent=body, fontSize=8.5, leading=11, spaceAfter=0)
    code = ParagraphStyle('CodePaper', fontName='Courier', fontSize=8.2, leading=11, leftIndent=9, spaceAfter=9)
    math = ParagraphStyle('EquationPaper', parent=body, fontSize=11, leading=18, leftIndent=12, spaceAfter=0)
    reference = ParagraphStyle('ReferencePaper', parent=body, fontSize=9.3, leading=12, spaceAfter=5)
    caption = ParagraphStyle('CaptionPaper', parent=body, keepWithNext=True)
    references_started = False
    lines = (ROOT/'paper.md').read_text().splitlines()
    story = []
    i=0
    while i < len(lines):
        line=lines[i]
        if not line.strip():
            i+=1
            continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]),title)); i+=1; continue
        if line.startswith('## '):
            if line == '## References':
                references_started = True
            story.append(Paragraph(inline(line[3:]),h2)); i+=1; continue
        if line.startswith('### '):
            story.append(Paragraph(inline(line[4:]),h3)); i+=1; continue
        if line.startswith('| '):
            rows=[]
            headers=[x.strip() for x in line.strip().strip('|').split('|')]
            while i<len(lines) and lines[i].startswith('|'):
                parts=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+',p) for p in parts):
                    rows.append([Paragraph(inline(p),cell) for p in parts])
                i+=1
            width=6.8*inch
            if headers == ['Operation', 'Actor class', 'Preconditions and effect', 'Energy cost']:
                fractions = [0.17,0.13,0.56,0.14]
            else:
                fractions = [0.15,0.27,0.29,0.29] if len(rows[0])==4 else [1/len(rows[0])]*len(rows[0])
            table=Table(rows,colWidths=[width*f for f in fractions],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf2')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),.4,colors.HexColor('#a7bac5')),('INNERGRID',(0,0),(-1,-1),.25,colors.HexColor('#bdccd4')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.extend([table,Spacer(1,10)]); continue
        if line.startswith('    '):
            block=[]
            while i<len(lines) and lines[i].startswith('    '):
                block.append(lines[i][4:]); i+=1
            if block[0].startswith('d(v,l) ='):
                story.append(KeepTogether([Paragraph(equation(row),math) for row in block] + [Spacer(1,9)]))
            else:
                story.append(Preformatted('\n'.join(block),code))
            continue
        block=[]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','    ')):
            block.append(lines[i].rstrip() + ('<BREAK>' if lines[i].endswith('  ') else '')); i+=1
            if re.match(r'^\d+\. ',block[-1]):
                break
        paragraph_style = reference if references_started else caption if block[0].startswith('**Table ') else body
        story.append(Paragraph(inline(' '.join(block)).replace('&lt;BREAK&gt;', '<br/>'),paragraph_style))
    out=ROOT/'output/pdf/controlling-incompatible-magic.pdf'
    out.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(out),pagesize=(8.5*inch,11*inch),leftMargin=.85*inch,rightMargin=.85*inch,topMargin=.72*inch,bottomMargin=.72*inch,title='Controlling Incompatible Magic',author="Tim O'Brien",subject='Research protocol preprint; model experiments pending')
    def footer(canvas,doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#c5d1d8'))
        canvas.line(.85*inch,.5*inch,7.65*inch,.5*inch)
        canvas.setFont('Helvetica',7)
        canvas.setFillColor(colors.HexColor('#52616b'))
        canvas.drawString(.85*inch,.34*inch,'Controlling Incompatible Magic | Research protocol v0.1.0')
        canvas.drawRightString(7.65*inch,.34*inch,str(doc.page))
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(out)


if __name__=='__main__':
    main()
