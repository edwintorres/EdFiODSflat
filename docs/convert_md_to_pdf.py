import markdown
import pdfkit

# Set the path explicitly
config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')  # Update this if needed

def md_to_pdf(md_file, output_pdf, css_file=None):
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Enable fenced code blocks for correct formatting
    html_content = markdown.markdown(md_content, extensions=['fenced_code'])

    # Apply CSS for better formatting (optional)
    options = {"encoding": "UTF-8"}
    if css_file:
        options["user-style-sheet"] = css_file

    pdfkit.from_string(html_content, output_pdf, options=options, configuration=config)

    print(f"✅ Conversion complete: {output_pdf}")

# Example usage
if __name__ == "__main__":
    md_to_pdf("pipelines/README.md", "PipelineReadMe.pdf", "style.css")
