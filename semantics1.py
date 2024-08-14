import antlr4 as antlr
from CoffeeLexer import CoffeeLexer
from CoffeeVisitor import CoffeeVisitor
from CoffeeParser import CoffeeParser
from CoffeeUtil import Var, Method, Import, Loop, SymbolTable

class CoffeeTreeVisitor(CoffeeVisitor):
    def __init__(self):
        self.stbl = SymbolTable()
        
    def visitProgram(self, ctx):
        line = ctx.start.line
        method =  Method('main', 'int', ctx.start.line)
        self.stbl.pushFrame(method)
        self.visitChildren(ctx)
        self.stbl.popFrame()
        
    def visitBlock(self, ctx):
        if (ctx.LCURLY() != None):
            self.stbl.pushScope()
        
        self.visitChildren(ctx)
        
        if (ctx.LCURLY() != None):
            self.stbl.popScope()
    
    # Semantic Rule 2: Global Variable declarations must have unique 
    # identifiers in a scope 
    
    def visitGlobal_decl(self, ctx):
        line = ctx.start.line
        var_type = ctx.var_decl().data_type().getText()
        
        for i in range(len(ctx.var_decl().var_assign())):            
            var_id = ctx.var_decl().var_assign(i).var().ID().getText()
            
            var_size = 8
            var_array = False
            
            var = self.stbl.peek(var_id)
            if (var != None):
                print("Error on line", line, "var", var_id, 
                      "already declared in scope on line" , var.line)
            
            # Checking for arrays
            if (ctx.var_decl().var_assign(i).var().INT_LIT() != None):
                var_size = int(ctx.var_decl().var_assign(i).var().INT_LIT().getText()) * 8
                var_array = True
                
                # Semantic Rule 14: Arrays must be declared with size greater than 0 
                if (var_size <= 0):
                    print("Cannot be a zero-length array declaration on line", line)            
            
            if (ctx.var_decl().var_assign(i).expr() != None):
                self.visit(ctx.var_decl().var_assign(i).expr())
            
            var = Var(var_id,
                      var_type,
                      var_size,
                      Var.GLOBAL,
                      var_array,
                      line)
            
            self.stbl.pushVar(var)
           

    # Semantic Rule 2: Local Variable declarations must have unique 
    # identifiers in a scope 
    
    def visitVar_decl(self, ctx):
        line = ctx.start.line
        var_type = ctx.data_type().getText()
        
        for i in range(len(ctx.var_assign())):         
            line = ctx.start.line
            var_id = ctx.var_assign(i).var().ID().getText()
            var_size = 8
            var_array = False
            
            var = self.stbl.peek(var_id)
            
            if (var != None):
                print("Error on line", line, "var", var_id, 
                      "already declared on line" , var.line)                
            
            # Checking for arrays
            if (ctx.var_assign(i).var().INT_LIT() != None):
                var_size = int(ctx.var_assign(i).var().INT_LIT().getText()) * 8
                var_array = True
                
                # Semantic Rule 14: Arrays must be declared with size greater than 0 
                if (var_size <= 0):
                    print("Cannot be a zero-length array declaration on line", line)
            
            if (ctx.var_assign(i).expr() != None):
                self.visit(ctx.var_assign(i).expr())
            
            var = Var(var_id,
                      var_type,
                      var_size,
                      Var.LOCAL,
                      var_array,
                      line)
            
            self.stbl.pushVar(var)
            
    
    def visitMethod_decl(self, ctx):
        line = ctx.start.line
        method_id = ctx.ID().getText()
        method_type = ctx.return_type().getText()
        
        # Semantic Rule 3: Method declarations (including imported methods)
        # must have a unique identifier in a scope
        
        method = self.stbl.peek(method_id)
        if (method != None):
            print("Error on line:", line, "method", method_id, 
                  "already declared on line", method.line)
        
        method = Method(method_id, method_type, line)
        
        self.stbl.pushMethod(method)
        self.stbl.pushFrame(method)
        
        for i in range(len(ctx.param())):
            var_id = ctx.param(i).ID().getText()
            var_type = ctx.param(i).data_type().getText()
            var_size = 8
            var_array = False

            var = self.stbl.peek(var_id)
            
            if (var != None):
                print("Error on line:", line, "method", method_id, 
                  "already declared on line", method.line)
                
            var = Var(var_id, 
                      var_type, 
                      var_size, 
                      Var.LOCAL, 
                      var_array, 
                      line)
            
            self.stbl.pushVar(var)
        
        method.pushParam(var_type)
        
        self.visit(ctx.block())
        
        # Semantic Rule 6: Void methods cannot return an expression
        if (method.has_return == True and method_type == 'void'):
            print("The method declared must not return a value" 
                  " on line", line)
        
        # Semantic Rule 7: Non-void methods must return an expression
        if (method.has_return == False and method_type != 'void'):
            print("The method declared on line", line, "must return a value",
                  method_type)
        
        self.stbl.popFrame()
        
    def visitReturn(self, ctx):
        line = ctx.start.line
        method_ctx = self.stbl.getMethodContext()
        method_ctx.has_return = True
        
        # type checking
        if (ctx.expr() != None):
            expr_type = self.visit(ctx.expr())
            
            if (expr_type != method_ctx.return_type):
                
                if (method_ctx.return_type != 'void'):
                    print("The method on line", line, "is returning", expr_type, 
                          "must be returning", method_ctx.return_type)
    
    def visitExpr(self, ctx):
        if (ctx.literal() != None):
            return self.visit(ctx.literal())
        
        elif (ctx.location() != None): 
            return self.visit(ctx.location())
        
        elif (len(ctx.expr()) == 2):
            # return high precedence type
            expr0_type = self.visit(ctx.expr(0))
            expr1_type = self.visit(ctx.expr(1))
            
            if (expr0_type != expr1_type):
                
                if (expr0_type == "float"):
                    expr1_type = "float"
                    return "float"
                
                elif (expr1_type == "float"):
                    expr0_type = "float"
                    return "float"
                
                elif (expr0_type == "int"):
                    expr1_type = "int"
                    return "int"
                
                elif (expr1_type == "int"):
                    expr0_type = "int"
                    return "int"

            else:
                return expr0_type
        
        elif (ctx.data_type() != None):
            return ctx.data_type
            
        else:
            return self.visitChildren(ctx)
            
            
    def visitLiteral(self, ctx):
        if (ctx.INT_LIT() != None):
            return 'int'
        elif (ctx.STRING_LIT() != None):
            return 'string'
        elif (ctx.FLOAT_LIT != None):
            return 'float'
        elif (ctx.CHAR_LIT != None):
            return 'char'
        elif (ctx.bool_lit != None):
            return 'bool'
            
    def visitLocation(self, ctx):
         var_id = ctx.ID().getText()
         var = self.stbl.find(var_id)
         line = ctx.start.line
         
         if (var != None):
             return var.data_type
         
         # Semantic Rule 1:  Variables must be declared before use
         else:
             print("Error on line ", line, "as variable is not declared.")


    def visitMethod_call(self, ctx):
        # get the method context from symbol table
        line = ctx.start.line
        method_ctx = self.stbl.getMethodContext()
        method_id = ctx.ID().getText()
        #method_type = ctx.return_type().getText()
        
        print(method_id)
        
        # get details and find method in symbol table
        method = self.stbl.peek(method_id)
        #method = Method(method_id, method_type, line)
        
        if (method == None):
            print("Error on line", line, "reference to undeclared method '" + method_id + "'")
        
        # check method call has same number of params
        
        
        # if method is import (no signature) show warning
        #for i in range(len(method.param)):
         #   expr_type = self.visit(ctx.expr(i))
          #  param_type = method.param[i]
           # print("Hi")
            
        # TODO: check types match, report errors...


            #if (expr_type != param_type):
            #   print("Error on line", line, "expr type is", expr_type, 
            #         "not same as parameter type", param_type)
                 
    
    # Semantic Rule 3: Method declarations (including imported methods) must 
    # have unique identifiers in a scope
    
    def visitImport_stmt(self, ctx):
        # gather details (method id, line, etc)
        line = ctx.start.line
        method_ctx = self.stbl.getMethodContext()
        method_id = ctx.ID()        
        
        # check symbol table for duplicates
        for i in range(len(method_id)):
            import_id = ctx.ID(i).getText()
            import_symbol = self.stbl.peek(import_id)

            if (import_symbol != None):
                print("Error on line", line, "import", import_id, 
                  "already declared on line", import_symbol.line)

            # add to symbol table    
            import_symbol = Import(import_id, 'int', line)
            
            self.stbl.pushMethod(import_symbol)
            
            
            
            
            
            
            
            
            
            
            
        
#load source code
filein = open('./test.coffee', 'r')
source_code = filein.read();
filein.close()

#create a token stream from source code
lexer = CoffeeLexer(antlr.InputStream(source_code))
stream = antlr.CommonTokenStream(lexer)

#parse token stream
parser = CoffeeParser(stream)
tree = parser.program()

#create Coffee Visitor object
visitor = CoffeeTreeVisitor()

#visit nodes from tree root
visitor.visit(tree)
