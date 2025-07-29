import aspose.words as aw

def create_test_docx():
    """Create a test DOCX file with CVE content for demonstration"""
    
    # Create new document
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    
    # Title
    builder.font.bold = True
    builder.font.size = 16
    builder.writeln("VMware ESXi Security Advisory")
    builder.font.bold = False
    builder.font.size = 12
    
    # Introduction paragraph
    builder.writeln()
    builder.writeln("VMware ESXi, vCenter Server, Workstation, and Fusion updates address multiple vulnerabilities including critical command execution flaws.")
    
    # CVE Details heading
    builder.writeln()
    builder.font.bold = True
    builder.font.size = 14
    builder.writeln("Vulnerability Details")
    builder.font.bold = False
    builder.font.size = 12
    
    # CVE description
    builder.writeln()
    builder.writeln("CVE-2025-41225 is an authenticated command-execution vulnerability in VMware vCenter Server that allows a privileged attacker to execute arbitrary commands. This type of CVE generally impacts system integrity and can lead to full administrative compromise if exploited in environments with inadequate privilege separation.")
    
    # CVSS table
    builder.writeln()
    builder.font.bold = True
    builder.writeln("CVSS Score Rating")
    builder.font.bold = False
    
    # Create table
    table = builder.start_table()
    
    # Header row
    builder.insert_cell()
    builder.font.bold = True
    builder.write("Severity")
    builder.insert_cell()
    builder.write("Low")
    builder.insert_cell()
    builder.write("Medium")
    builder.insert_cell()
    builder.write("High")
    builder.insert_cell()
    builder.write("Critical")
    builder.end_row()
    
    # Score row
    builder.insert_cell()
    builder.font.bold = True
    builder.write("CVSS Score")
    builder.font.bold = False
    builder.insert_cell()
    builder.write("0.1-3.9")
    builder.insert_cell()
    builder.write("4.0-6.9")
    builder.insert_cell()
    builder.write("7.0-8.9")
    builder.insert_cell()
    builder.write("✓ 9.0-10.0")
    builder.end_row()
    
    builder.end_table()
    
    # Security Impact section
    builder.writeln()
    builder.font.bold = True
    builder.font.size = 14
    builder.writeln("Security Impact")
    builder.font.bold = False
    builder.font.size = 12
    
    builder.writeln()
    builder.writeln("An attacker with sufficient permission could leverage this flaw to execute unauthorized commands, potentially leading to data breaches, lateral movement, or service disruption, undermining both confidentiality and system control.")
    
    # Products Affected
    builder.writeln()
    builder.font.bold = True
    builder.writeln("Products Affected:")
    builder.font.bold = False
    
    builder.writeln("• VMware ESXi")
    builder.writeln("• VMware vCenter Server")
    builder.writeln("• VMware Workstation Pro")
    builder.writeln("• VMware Fusion")
    
    # Publication info
    builder.writeln()
    builder.writeln("Publication date: 20 May 2025")
    builder.writeln("CVSSv3 Score Range: 4.3 – 8.8")
    
    # Save document
    doc.save("test_cve_document.docx", aw.SaveFormat.DOCX)
    print("Created test_cve_document.docx")

if __name__ == "__main__":
    create_test_docx()