const fs = require('fs');
const parser = require('@babel/parser');

const fileContent = fs.readFileSync('src/components/custom/AddModuleForm.tsx', 'utf-8');

try {
  parser.parse(fileContent, {
    sourceType: 'module',
    plugins: ['jsx', 'typescript']
  });
  console.log("No syntax errors found by Babel.");
} catch (e) {
  console.error("Syntax Error:", e.message);
  console.error("Location:", e.loc);
  
  if (e.loc) {
    const lines = fileContent.split('\n');
    const startLine = Math.max(0, e.loc.line - 5);
    const endLine = Math.min(lines.length - 1, e.loc.line + 5);
    for (let i = startLine; i <= endLine; i++) {
        const prefix = (i + 1 === e.loc.line) ? '> ' : '  ';
        console.log(`${prefix}${i + 1} | ${lines[i]}`);
    }
  }
}
