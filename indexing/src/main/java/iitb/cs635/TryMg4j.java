package iitb.cs635;

import it.unimi.di.mg4j.document.FileSetDocumentCollection;
import it.unimi.di.mg4j.query.HttpFileServer;
import it.unimi.di.mg4j.query.Query;
import it.unimi.di.mg4j.tool.IndexBuilder;
import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import org.apache.commons.io.FileUtils;

public class TryMg4j {
    /**
     * Indexes a directory of HTML document files.
     * From command line, this can be run as
     * mvn exec:java -Dexec.mainClass="iitb.cs635.TryMg4j"
     *     -Dexec.args="corpus index"
     * (make sure a folder with name index exists before running)
     * Then visit http://localhost:4242/Query
     * @param args [1]=/path/to/corpus/dir [2]=/path/to/index/dir
     * @throws Exception 
     */
    public static void main(String args[]) throws Exception {
        final String corpusPath = args[0], indexPath = args[1];
        final File corpusDir = new File(corpusPath),
                indexDir = new File(indexPath);
        assert corpusDir.isDirectory() && indexDir.isDirectory();
        Collection<File> docFiles =
                FileUtils.listFiles(corpusDir, new String[]{"txt"}, false);
        ArrayList<String> mg4jArgs = new ArrayList<>();
        mg4jArgs.add("-f");
        mg4jArgs.add("it.unimi.di.mg4j.document.tika.TextDocumentFactory");
        final File collectionFile = new File(indexDir, "corpus.collection");
        mg4jArgs.add(collectionFile.getAbsolutePath());
        for (File docFile : docFiles) {
            mg4jArgs.add(docFile.getAbsolutePath());
        }
        FileSetDocumentCollection.main(mg4jArgs.toArray(new String[]{}));
        IndexBuilder.main(new String[]{
            "-S", collectionFile.getAbsolutePath(),
            (new File(indexDir, "cs635")).getAbsolutePath()
        });

        Query.main(new String[]{
            "-h", "-i", "iitb.cs635.FileResource",
            "-c", collectionFile.getAbsolutePath(),
            (new File(indexDir, "cs635-text")).getAbsolutePath()            
        });
    }
}