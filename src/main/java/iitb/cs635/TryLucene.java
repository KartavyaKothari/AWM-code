package iitb.cs635;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.RAMDirectory;

import java.io.IOException;

	public class TryLucene {
	public static void main(String[] args) 
                throws IOException, ParseException
        {
	    StandardAnalyzer analyzer = new StandardAnalyzer();
	    Directory index = new RAMDirectory();
	
	    IndexWriterConfig config = new IndexWriterConfig(analyzer);
	
	    IndexWriter w = new IndexWriter(index, config);
	    addDoc(w, "Lucene in Action", "1");
	    addDoc(w, "Lucene for Dummies", "2");
	    addDoc(w, "Java", "3");
	    addDoc(w, "Oracle", "4");
	    w.close();
	
	    String querystr = "java";
	
	    Query q = new QueryParser("title", analyzer).parse(querystr);
	
	    int hitsPerPage = 10;
	    IndexReader reader = DirectoryReader.open(index);
	    IndexSearcher searcher = new IndexSearcher(reader);
	    TopScoreDocCollector collector = TopScoreDocCollector.create(hitsPerPage);
	    searcher.search(q, collector);
	    ScoreDoc[] hits = collector.topDocs().scoreDocs;
	    
	    System.out.println("Found " + hits.length + " hits.");
	    for(int i=0;i<hits.length;++i) {
	      int docId = hits[i].doc;
	      Document d = searcher.doc(docId);
	      System.out.println("docid=" + docId + " isbn=" + d.get("isbn") + " title=" + d.get("title"));
	    }
	    reader.close();
	  }
	
	  private static void addDoc(IndexWriter w, String title, String isbn) throws IOException {
	    Document doc = new Document();
	    doc.add(new TextField("title", title, Field.Store.YES));
	    doc.add(new StringField("isbn", isbn, Field.Store.YES));
	    w.addDocument(doc);
	  }
}