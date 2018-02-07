package iitb.cs635;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.handler.ContextHandler;
import org.eclipse.jetty.server.handler.ResourceHandler;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class FileResource extends HttpServlet {
    static int port = Integer.parseInt(System.getProperty(FileResource.class.getName()+".port", "8080"));

    public static int getPort() {
        return port;
    }

    static{
        Server server = new Server(port);

        //1.Creating the resource handler
        ResourceHandler resourceHandler= new ResourceHandler();

        //2.Setting FileResource Base
        resourceHandler.setResourceBase("/");

        //3.Enabling Directory Listing
        resourceHandler.setDirectoriesListed(true);

        //4.Setting Context Source
        ContextHandler contextHandler= new ContextHandler("/");

        //5.Attaching Handlers
        contextHandler.setHandler(resourceHandler);
        server.setHandler(contextHandler);

        // Starting the Server

        (new Thread(() -> {
            try {
                server.start();
                System.out.println("Started!");
                server.join();
            } catch (Exception e) {
                System.err.println("Exception while starting the file server");
                throw new RuntimeException();
            }
        })).start();
    }

    protected void doGet(final HttpServletRequest request, final HttpServletResponse response ) throws IOException {

        String uri = request.getParameter( "uri" );
        if ( uri != null && uri.indexOf( "file:" ) == 0 ) {
            uri = uri.substring( "file:".length() );
            response.setStatus( HttpServletResponse.SC_MOVED_PERMANENTLY );
            response.addHeader( "location", "http://localhost:" + getPort() + uri );
            return;
        }

        response.sendError( HttpServletResponse.SC_FORBIDDEN, "This servlet requires a parameter uri containing a URI of type file:" );
    }

    protected void doPost( final HttpServletRequest request, final HttpServletResponse response ) throws IOException {
        doGet( request, response );
    }
}
