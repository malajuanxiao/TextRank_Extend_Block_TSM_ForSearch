import entity.Que;
import entity.Result;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.apache.solr.common.util.NamedList;
import org.junit.Test;
import org.wltea.analyzer.lucene.IKAnalyzer;
import support.fetchTestData;
import support.showResult;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class TestSolr2 {

    private final static String SOLR_URL = "http://localhost:8395/solr/";
    private final static String coreName = "new_test";
    HttpSolrClient solrServer = new HttpSolrClient.Builder(SOLR_URL+coreName).build();


    @Test
    public void queryDocForTrec() throws IOException, ParseException, SolrServerException {

        List<Que> queryList = fetchTestData.fetchQuery();
        int start = 150;
        int end = 249;
        queryList = queryList.subList(start,end);


        for(Que que : queryList){
            //查询，获取分数列表
            //que.setResultList(getQueryResult(que,query));
            //System.out.println("enter");

            SolrQuery query = new SolrQuery();
            //query.setFields("content");

            //query.set("q", "china");
            query.setStart(0);
            query.setRows(1000);//每一页多少值
            query.set("q", que.getTitle().replace(":","") +" "+ que.getDesc().replace(":",""));//防止冒号引起的域定义歧义
            query.set("df", "content");
            //query.set("df", "default_search");
            //System.out.println(query.get("df") +  que.getTitle() +" "+ que.getDesc());


            //获取查询结果
            QueryResponse response = solrServer.query(query);
            List<Result> resultList = new ArrayList<>();
            float sort_rank = 0;

            //查询得到文档的集合
            SolrDocumentList solrDocumentList = response.getResults();

            //遍历列表
            for (SolrDocument doc : solrDocumentList) {
                String doc_no = doc.get("doc_no").toString();
                resultList.add(new Result(sort_rank++, doc_no.substring(1,doc_no.length()-1)) );
                //System.out.println("id:"+doc.get("id")+" docno:"+doc.get("doc_no"));
            }
            //System.out.println(resultList);
            que.setResultList(resultList);



            //break;
        }

        showResult sr = new showResult();
        sr.getPR(queryList,5,2);
        System.out.println(sr.getMeanPresion());
        System.out.println(sr.getMAP(queryList,200,20));




    }


}
