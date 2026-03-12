# Grammar Specification (Sprint 2)

## Notation
EBNF (Extended Backus-Naur Form)

## Precedence (highest to lowest)
1. Primary: literals, identifiers, parenthesized expressions
2. Unary: -, !
3. Multiplicative: *, /, %
4. Additive: +, -
5. Relational: <, <=, >, >=
6. Equality: ==, !=
7. Logical AND: &&
8. Logical OR: ||
9. Assignment: =

## Associativity
- Left: + - * / % && || == != < <= > >=
- Right: =

## Grammar Rules

Program        ::= { Declaration }
Declaration    ::= FunctionDecl | StructDecl | VarDecl
FunctionDecl   ::= "fn" Identifier "(" [ Parameters ] ")" [ "->" Type ] Block
StructDecl     ::= "struct" Identifier "{" { VarDecl } "}" ";"
VarDecl        ::= Type Identifier [ "=" Expression ] ";"

Statement      ::= Block | IfStmt | WhileStmt | ForStmt | ReturnStmt | ExprStmt
Block          ::= "{" { Statement } "}"
IfStmt         ::= "if" "(" Expression ")" Statement [ "else" Statement ]
WhileStmt      ::= "while" "(" Expression ")" Statement
ForStmt        ::= "for" "(" [ ExprStmt ] ";" [ Expression ] ";" [ Expression ] ")" Statement
ReturnStmt     ::= "return" [ Expression ] ";"
ExprStmt       ::= Expression ";"

Expression     ::= Assignment
Assignment     ::= LogicalOr [ ( "=" ) Assignment ]
LogicalOr      ::= LogicalAnd { "||" LogicalAnd }
LogicalAnd     ::= Equality { "&&" Equality }
Equality       ::= Relational { ( "==" | "!=" ) Relational }
Relational     ::= Additive { ( "<" | "<=" | ">" | ">=" ) Additive }
Additive       ::= Multiplicative { ( "+" | "-" ) Multiplicative }
Multiplicative ::= Unary { ( "*" | "/" | "%" ) Unary }
Unary          ::= [ ( "-" | "!" ) ] Primary
Primary        ::= Literal | Identifier | "(" Expression ")" | Call
Call           ::= Primary "(" [ Arguments ] ")"
Arguments      ::= Expression { "," Expression }

Type           ::= "int" | "float" | "bool" | "void" | Identifier
Parameters     ::= Parameter { "," Parameter }
Parameter      ::= Type Identifier
Literal        ::= Integer | Float | String | Boolean