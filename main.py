from classes.Application import Application

app = Application("assets/taz.jpg")

app.bind("<Button-1>", app.select_handle)
app.bind("<ButtonRelease-1>", app.deselect_handle)
app.bind("<Button-3>", app.remove_handle)
app.bind("<B1-Motion>", app.move_handle)

app.run()

