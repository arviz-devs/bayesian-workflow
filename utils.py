def print_stan(model):
    """Print Stan code from a CmdStanModel with syntax highlighting"""
    code = model.code()
    
    try:
        get_ipython()
        from IPython.display import Markdown, display
        display(Markdown(f"```stan\n{code}\n```"))
    except NameError:
        print(code)