export function formatExpression(expression: string) {
  let indentLevel = 0;
  let formattedExpression = "";
  let currentLine = "";

  for (const char of expression) {
    switch (char) {
      case "(":
        formattedExpression +=
          currentLine + char + "\n" + " ".repeat(indentLevel * 2);
        indentLevel++;
        currentLine = " ".repeat(indentLevel * 2);
        break;
      case ")":
        if (currentLine.trim() !== "") {
          formattedExpression += currentLine + "\n";
        }
        indentLevel--;
        formattedExpression += " ".repeat(indentLevel * 2) + char;
        currentLine = "";
        break;
      default:
        currentLine += char;
        break;
    }
  }

  return formattedExpression;
}
