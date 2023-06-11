import express, { Express, Response, Request } from "express";
import serveStatic from 'serve-static';
import path from "path";

const app: Express = express();

app.use(serveStatic(path.resolve(__dirname, '../public')));

app.get('/', (request: Request, response: Response) => {
    response.sendFile('views/home.html', {root: __dirname});
});

app.get('*', (request: Request, response: Response) => {
    response.redirect('/');
});

app.listen(8080, () => {
    console.log("Server started on port 8080.");
})
