"""
导出管理模块
支持 Markdown 和 PDF 格式导出
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import markdown
from weasyprint import HTML

from config import settings

logger = logging.getLogger(__name__)


class ExportManager:
    """导出管理类"""
    
    def __init__(self, output_dir: Path = None):
        """
        初始化导出管理器
        
        Args:
            output_dir: 输出目录，默认使用配置值
        """
        self.output_dir = output_dir or settings.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, topic: str, extension: str) -> str:
        """
        生成文件名
        
        Args:
            topic: 研究主题
            extension: 文件扩展名 (不含点)
            
        Returns:
            str: 文件名
        """
        # 清理主题名称，移除特殊字符
        safe_topic = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_' 
            for c in topic
        )
        safe_topic = safe_topic.strip()[:50]  # 限制长度
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{safe_topic}_{timestamp}.{extension}"
    
    def export_markdown(self, content: str, topic: str, filename: str = None) -> Path:
        """
        导出为 Markdown 文件
        
        Args:
            content: Markdown 内容
            topic: 研究主题
            filename: 自定义文件名（可选）
            
        Returns:
            Path: 导出的文件路径
        """
        if not filename:
            filename = self._generate_filename(topic, "md")
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Markdown 导出成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Markdown 导出失败: {str(e)}")
            raise
    
    def export_pdf(self, content: str, topic: str, filename: str = None) -> Path:
        """
        导出为 PDF 文件
        
        Args:
            content: Markdown 内容
            topic: 研究主题
            filename: 自定义文件名（可选）
            
        Returns:
            Path: 导出的文件路径
        """
        if not filename:
            filename = self._generate_filename(topic, "pdf")
        
        filepath = self.output_dir / filename
        
        try:
            # 将 Markdown 转换为 HTML
            html_content = markdown.markdown(
                content,
                extensions=['extra', 'codehilite', 'toc']
            )
            
            # 添加 CSS 样式
            styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            margin: 2cm;
            size: A4;
        }}
        body {{
            font-family: "Microsoft YaHei", "SimSun", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
            margin-top: 25px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            color: #666;
            margin: 15px 0;
        }}
        ul, ol {{
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
            
            # 转换为 PDF
            HTML(string=styled_html).write_pdf(filepath)
            
            logger.info(f"PDF 导出成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"PDF 导出失败: {str(e)}")
            raise
    
    def export_both(self, content: str, topic: str) -> tuple[Path, Path]:
        """
        同时导出 Markdown 和 PDF
        
        Args:
            content: Markdown 内容
            topic: 研究主题
            
        Returns:
            tuple: (markdown_path, pdf_path)
        """
        base_filename = self._generate_filename(topic, "")
        base_filename = base_filename[:-1]  # 移除最后的点
        
        md_path = self.export_markdown(content, topic, f"{base_filename}.md")
        pdf_path = self.export_pdf(content, topic, f"{base_filename}.pdf")
        
        return md_path, pdf_path
