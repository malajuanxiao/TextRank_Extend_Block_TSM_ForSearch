import entity.Que;
import entity.Result;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.wltea.analyzer.lucene.IKAnalyzer;
import support.fetchTestData;

import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.search.*;
import org.apache.lucene.store.FSDirectory;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import support.showResult;

public class batchQuery {
    public static void main(String[] args) throws IOException, ParseException {

        List<Que> queryList = fetchTestData.fetchQuery();
        //int start = 150;
        //int end = 249;
        //queryList = queryList.subList(start,end);

        for(Que query : queryList){
            //查询，获取分数列表
            query.setResultList(getQueryResult(query));
        }
        showResult sr = new showResult();
        sr.getPR(queryList,5,2);
        System.out.println(sr.getMeanPresion());
        System.out.println(sr.getMAP(queryList,200,20));



        //testMatchAll();
    }

    public static List<Result> getQueryResult(Que que) throws IOException, ParseException {
        //String indexPath = "E:\\Indexfile\\lucene\\Index1";
        String indexPath = "E:\\Indexfile\\lucene\\IndexTrec";
        DirectoryReader directoryReader = DirectoryReader.open(FSDirectory.open(Paths.get(indexPath)));
        IndexSearcher indexSearcher = new IndexSearcher(directoryReader);

        //多字段的查询转换器
        String[] fields = {"title", "content"};
        Analyzer analyzer = new IKAnalyzer(true);
        MultiFieldQueryParser queryParser = new MultiFieldQueryParser(fields, analyzer);
        String querystr = que.getTitle() +" "+ que.getDesc(); //System.out.println(querystr);
        Query query = queryParser.parse(querystr);

        //按分数排序
        List<Result> resultList = new ArrayList<>();
        TopDocs topDocs = indexSearcher.search(query, 1000);
        ScoreDoc[] scoreDocs = topDocs.scoreDocs;
        System.out.println(que.getId()+": 获取结果条数 "+scoreDocs.length);

        for (ScoreDoc scoreDoc : scoreDocs) {
            resultList.add(new Result(scoreDoc.score,indexSearcher.doc(scoreDoc.doc).get("doc_no"))  );
        }
        //System.out.println(resultList);

        directoryReader.close();
        return resultList;
    }



    public static void testMatchAll() throws IOException, ParseException {

        //String indexPath = "E:\\Indexfile\\lucene\\Index";
        String indexPath = "E:\\Indexfile\\lucene\\IndexTrec";
        DirectoryReader directoryReader = DirectoryReader.open(FSDirectory.open(Paths.get(indexPath)));
        IndexSearcher indexSearcher = new IndexSearcher(directoryReader);
        Query query = new MatchAllDocsQuery();

        Sort sort = new Sort(new SortField("id", SortField.Type.DOC, true));
        TopDocs topDocs = indexSearcher.search(query, 10, sort);
        ScoreDoc[] scoreDocs = topDocs.scoreDocs;
        for (ScoreDoc scoreDoc : scoreDocs) {
            int doc = scoreDoc.doc;
            System.out.println(doc);
        }


        directoryReader.close();
    }
}


