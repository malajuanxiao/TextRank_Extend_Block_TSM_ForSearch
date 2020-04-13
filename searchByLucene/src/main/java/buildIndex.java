import parse.*;
import entity.Article;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.FSDirectory;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.io.*;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import java.nio.file.Paths;

public class buildIndex {
    public static long id = 396259;

    public static void main(String[] args) throws IOException{
        String indexPath = "E:\\Indexfile\\lucene\\IndexTrec";
        //String indexPath = "E:\\Indexfile\\lucene\\trecIndex";
        FSDirectory fsDirectory = FSDirectory.open(Paths.get(indexPath));
        //创建一个标准分词器，一个字分一次
        Analyzer analyzer = new StandardAnalyzer();
        //写入索引的配置，设置了分词器
        IndexWriterConfig indexWriterConfig = new IndexWriterConfig(analyzer);
        //指定了写入数据目录和配置
        IndexWriter indexWriter = new IndexWriter(fsDirectory, indexWriterConfig);

        //directoryFind("FT",indexWriter);
        //directoryFind("FBIS",indexWriter);
        directoryFind("LATIMES",indexWriter);
        //directoryFind("FR94",indexWriter);
        indexWriter.close();
    }


    public static void directoryFind(String dataName,IndexWriter indexWriter) throws IOException {
        File file = new File( "E:\\Indexfile\\disk\\TREC\\" + dataName);
        if (file.exists()) {
            File[] files = file.listFiles();
            if (null != files) {
                for (File file2 : files) {
                    if (file2.isDirectory()) {
                        //System.out.println("文件夹:" + file2.getAbsolutePath());
                        directoryFind(dataName + '\\' + file2.getName(),indexWriter);
                    } else {
                        //System.out.println("文件:" + file2.getAbsolutePath());
                        //System.out.println("文件名:" + file2.getName());
                        List<Article> articleList = new ArrayList<>();
                        //articleList = testFBParse(file2);
                        //articleList = testFTParse(file2);
                        //articleList = testFR94Parse(file2);
                        //articleList = testLAParse(file2);

                        if (dataName.equals("FT")){
                            articleList = testFTParse(file2);
                        }else if(dataName.equals("LATIMES")){
                            articleList = testLAParse(file2);
                        }else if(dataName.equals("FBIS")){
                            articleList = testFBParse(file2);
                        }else {
                            articleList = testFR94Parse(file2);
                        }

                        for(Article article : articleList){
                            article.setId(id++);
                            if(article.getTitle() == null){
                                article.setTitle("");
                            }
                            if(article.getContent() == null){
                                article.setContent("");
                            }
                            //创建一个文档对象通过IndexWriter写入
                            Document document = article.toDocument();
                            indexWriter.addDocument(document);
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
