
import java.io.*;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import entity.Article;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.util.NamedList;
import org.junit.Test;
import parse.FBHandler;
import parse.FRHandler;
import parse.FTHandler;
import parse.LAHandler;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;


public class TestSolr {
    public static long id = 0;
    private final static String SOLR_URL = "http://localhost:8395/solr/";
    private final static String coreName = "new_test";


    /**
     * 往索引库添加文档
     * @throws IOException
     * @throws SolrServerException
     */
    @Test
    public void addDoc() throws SolrServerException, IOException {
        //获得一个solr服务端的请求，去提交  ,选择具体的某一个solr core
        //solr的服务器地址
        //private final static String SOLR_URL = "http://localhost:8080/solr/";
        HttpSolrClient solrServer = new HttpSolrClient.Builder(SOLR_URL+coreName).build();
        try {
            //构造一篇文档
            SolrInputDocument document = new SolrInputDocument();
            //往doc中添加字段,在客户端这边添加的字段必须在服务端中有过定义
            document.addField("id", "1");
            document.addField("doc_no", "FT_001");
            document.addField("title", "testDoc1");
            document.addField("content", "I love china");
            solrServer.add(document);

            solrServer.commit();
        } finally{
            solrServer.close();
        }

    }





    @Test
    public void queryDoc() throws SolrServerException, IOException {
        //获得一个solr服务端的请求，去提交  ,选择具体的某一个solr core
        //solr的服务器地址
        //private final static String SOLR_URL = "http://localhost:8080/solr/";
        HttpSolrClient solrServer = new HttpSolrClient.Builder(SOLR_URL+coreName).build();
        SolrQuery query = new SolrQuery();
        query.set("df", "content");
        query.set("q", "china");
        //query.setSort("id",SolrQuery.ORDER.desc);//参数sort,设置返回结果的排序规则


        //query.set("q", "*:*");// 参数q  查询所有
        //query.set("q","好");//相关查询，比如某条数据某个字段含有某个字  将会查询出来 ，这个作用适用于联想查询

        //参数fq, 给query增加过滤查询条件
        //query.addFilterQuery("id:[0 TO 9]");//id为0-9




        //设置分页参数
        query.setStart(0);
        query.setRows(10);//每一页多少值
        //参数hl,设置高亮
        query.setHighlight(true);
        //设置高亮的字段
        query.addHighlightField("content");
        //设置高亮的样式
        query.setHighlightSimplePre("<font color='red'>");
        query.setHighlightSimplePost("</font>");


        //获取查询结果
        QueryResponse response = solrServer.query(query);
        //两种结果获取：得到文档集合或者实体对象

        //查询得到文档的集合
        SolrDocumentList solrDocumentList = response.getResults();
        //NamedList，一个有序的name/value容器，NamedList不像Map
        NamedList list = (NamedList) response.getResponse().get("highlighting");
        System.out.println(list);
        System.out.println("查询的结果");
        System.out.println("总数量：" + solrDocumentList.getNumFound());
        //遍历列表
        for (SolrDocument doc : solrDocumentList) {
            System.out.println("id:"+doc.get("id")+" title:"+doc.get("title")+" content:"+doc.get("content"));
        }

    }
    @Test
    public void delDoc() throws SolrServerException, IOException {
        //获得一个solr服务端的请求，去提交  ,选择具体的某一个solr core
        //solr的服务器地址
        //private final static String SOLR_URL = "http://localhost:8080/solr/";
        HttpSolrClient solrServer = new HttpSolrClient.Builder(SOLR_URL+coreName).build();
        //删除文档
        //solrServer.deleteById("1");
        //删除所有的索引
        solrServer.deleteByQuery("*:*");
        //提交修改
        solrServer.commit();
        solrServer.close();

    }



    @Test
    public void addDocForTrec() throws SolrServerException, IOException {

        HttpSolrClient solrServer = new HttpSolrClient.Builder(SOLR_URL+coreName).build();
        //directoryFind("FT",solrServer);

        //directoryFind("FBIS",solrServer);
        //directoryFind("FR94",solrServer);
        directoryFind("LATIMES",solrServer);
        solrServer.close();

    }


    public static void directoryFind(String dataName,HttpSolrClient solrServer) throws IOException, SolrServerException {
        List<Article> articleList = new ArrayList<>();
        //SolrInputDocument document = new SolrInputDocument();
        File file = new File( "E:\\Indexfile\\disk\\TREC\\" + dataName);
        if (file.exists()) {
            File[] files = file.listFiles();
            if (null != files) {
                for (File file2 : files) {
                    if (file2.isDirectory()) {
                        //System.out.println("文件夹:" + file2.getAbsolutePath());
                        directoryFind(dataName + '\\' + file2.getName(),solrServer);
                    } else {



                        //System.out.println("文件:" + file2.getAbsolutePath());
                        //System.out.println("文件名:" + file2.getName());

                        //articleList = testFBParse(file2);
                        //articleList = testFTParse(file2);
                        //articleList = testFR94Parse(file2);
                        articleList = testLAParse(file2);

                        for(Article article : articleList){
                            article.setId(id++);
                            if(article.getTitle() == null){
                                article.setTitle("");
                            }
                            if(article.getContent() == null){
                                article.setContent("");
                            }
                            //往doc中添加字段,在客户端这边添加的字段必须在服务端中有过定义
                            //document.addField("id", Long.valueOf(article.getId()) );
                            SolrInputDocument document = new SolrInputDocument();
                            document.addField("doc_no", article.getDoc_no());
                            document.addField("title", article.getTitle());
                            document.addField("content", article.getContent());
                            solrServer.add(document);
                            solrServer.commit();

                        }
                    }
                }
            }
        } else {
            System.out.println("文件不存在!");
        }

    }


    public static List<Article>  testFTParse(File file){
        List<Article> articleList = new ArrayList<>();
        File readfile = file;
        File loadfile = new File("E:\\Indexfile\\disk\\TREC\\test\\" + file.getName());
        Pattern r1 = Pattern.compile("&(.*);");
        System.out.println(file.getAbsolutePath() + "testFTParse");

        try {
            BufferedReader in = new BufferedReader(new FileReader(readfile));
            PrintWriter out = new PrintWriter(new FileWriter(loadfile));

            String str = in.readLine();
            while(str!=null) {
                str = str.trim();

                Matcher m1 = r1.matcher(str);
                if (m1.find()){
                    str = m1.replaceAll(" ");
                }

                if (str != null && !str.equals("") && !str.equals("\n")) {
                    if(str.toCharArray()[0]=='<'){
                        out.println(str);
                    }else{
                        out.print(str.replace("\n"," "));
                    }
                }

                str = in.readLine();
            }
            in.close();
            out.close();
        }catch(FileNotFoundException e1) {
            System.err.println("File not found");
        }catch(IOException e2) {
            e2.printStackTrace();
        }


        try {
            SAXParserFactory spf = SAXParserFactory.newInstance();
            SAXParser parser = spf.newSAXParser();
            FTHandler handler = new FTHandler("DOC");
            FileInputStream input = new FileInputStream(loadfile);
            parser.parse(input, handler);
            input.close();
            articleList = handler.getArticles(); //for(Article article: articleList){ System.out.println(article.toString());}
        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return articleList;
    }



    public static List<Article> testFR94Parse(File file){
        List<Article> articleList = new ArrayList<>();
        File readfile = file;
        File loadfile = new File("E:\\Indexfile\\disk\\TREC\\test\\" + file.getName());
        Pattern r1 = Pattern.compile("<!--(.*)-->");
        Pattern r2 = Pattern.compile("&(.*);");
        Pattern r3 = Pattern.compile("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"");
        Pattern r4 = Pattern.compile("\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">");
        System.out.println(file.getAbsolutePath() + "testFR94Parse");
        try {
            BufferedReader in = new BufferedReader(new FileReader(readfile));
            PrintWriter out = new PrintWriter(new FileWriter(loadfile));

            String str = in.readLine();
            while(str!=null) {
                //System.out.println("enter");
                str = str.trim();
                // 现在创建 matcher 替换xml文件中的注释
                Matcher m1 = r1.matcher(str);
                if (m1.find()) {
                    str = m1.replaceAll("");
                }
                Matcher m2 = r2.matcher(str);
                if (m2.find()){
                    str = m2.replaceAll(" ");
                }

                Matcher m3 = r3.matcher(str);
                if (m3.find()){
                    str = m3.replaceAll("");
                }
                Matcher m4 = r4.matcher(str);
                if (m4.find()){
                    str = m4.replaceAll("");
                }


                if (str != null && !str.equals("") && !str.equals("\n")) {
                    if(str.toCharArray()[0]=='<'){
                        out.println(str);
                    }else{
                        out.print(str.replace("\n"," "));
                    }
                }
                str = in.readLine();
            }
            in.close();
            out.close();
        }catch(FileNotFoundException e1) {
            System.err.println("File not found");
        }catch(IOException e2) {
            e2.printStackTrace();
        }

        try {
            SAXParserFactory spf = SAXParserFactory.newInstance();
            SAXParser parser = spf.newSAXParser();
            FRHandler handler = new FRHandler("DOC");
            FileInputStream input = new FileInputStream(loadfile);
            parser.parse(input, handler);
            input.close();
            articleList= handler.getArticles();//for(Article article: articleList){ System.out.println(article.toString());}
        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return articleList;
    }


    public static List<Article> testFBParse(File file){
        List<Article> articleList = new ArrayList<>();
        File readfile = file;
        File loadfile = new File("E:\\Indexfile\\disk\\TREC\\test\\" + file.getName());
        Pattern r1 = Pattern.compile("&(.*);");
        Pattern r2 = Pattern.compile("P=(\\d+)");
        Pattern r3 = Pattern.compile("<FIG ID=(.*)>");
        Pattern r4 = Pattern.compile("&");
        System.out.println(file.getAbsolutePath() + "testFBParse");

        try {
            BufferedReader in = new BufferedReader(new FileReader(readfile));
            PrintWriter out = new PrintWriter(new FileWriter(loadfile));

            String str = in.readLine();
            while(str!=null) {
                str = str.trim();

                Matcher m1 = r1.matcher(str);
                if (m1.find()){
                    str = m1.replaceAll(" ");
                }

                Matcher m2 = r2.matcher(str);
                if (m2.find()){
                    str = m2.replaceAll(" ");
                }

                Matcher m3 = r3.matcher(str);
                if (m3.find()){
                    str = m3.replaceAll(" ");
                }

                Matcher m4 = r4.matcher(str);
                if (m4.find()){
                    str = m4.replaceAll(" ");
                }

                if (str != null && !str.equals("") && !str.equals("\n")) {
                    if(str.toCharArray()[0]=='<'){
                        out.println(str);
                    }else{
                        out.print(str.replace("\n"," "));
                    }
                }
                str = in.readLine();
            }
            in.close();
            out.close();
        }catch(FileNotFoundException e1) {
            System.err.println("File not found");
        }catch(IOException e2) {
            e2.printStackTrace();
        }


        try {
            SAXParserFactory spf = SAXParserFactory.newInstance();
            SAXParser parser = spf.newSAXParser();
            FBHandler handler = new FBHandler("DOC");
            FileInputStream input = new FileInputStream(loadfile);
            parser.parse(input, handler);
            input.close();
            articleList = handler.getArticles();//for(Article article: articleList){ System.out.println(article.toString());}
        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return  articleList;
    }


    public static List<Article> testLAParse(File file) {
        List<Article> articleList = new ArrayList<>();
        File readfile = file;
        File loadfile = new File("E:\\Indexfile\\disk\\TREC\\test\\" + file.getName());
        Pattern r1 = Pattern.compile("&(.*);");
        System.out.println(file.getAbsolutePath() + "testLAParse");

        try {
            BufferedReader in = new BufferedReader(new FileReader(readfile));
            PrintWriter out = new PrintWriter(new FileWriter(loadfile));

            String str = in.readLine();
            while(str!=null) {
                str = str.trim();
                Matcher m1 = r1.matcher(str);
                if (m1.find()){
                    str = m1.replaceAll(" ");
                }

                if (str != null && !str.equals("") && !str.equals("\n")) {
                    if(str.toCharArray()[0]=='<'){
                        out.println(str);
                    }else{
                        out.print(str.replace("\n"," "));
                    }
                }
                str = in.readLine();
            }
            in.close();
            out.close();
        }catch(FileNotFoundException e1) {
            System.err.println("File not found");
        }catch(IOException e2) {
            e2.printStackTrace();
        }

        try {
            SAXParserFactory spf = SAXParserFactory.newInstance();
            SAXParser parser = spf.newSAXParser();
            LAHandler handler = new LAHandler("DOC");
            FileInputStream input = new FileInputStream(loadfile);
            parser.parse(input, handler);
            input.close();
            articleList = handler.getArticles();
        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return articleList;
    }
}


