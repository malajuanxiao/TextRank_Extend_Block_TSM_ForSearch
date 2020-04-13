package parse;

import entity.Article;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import java.util.ArrayList;
import java.util.List;

public class LAHandler extends DefaultHandler {
    private List<Article> articles = null;
    private Article article;
    private String currentTag = null;
    private String currentValue = null;
    private String currentParentTag = "";
    private String nodeName = null;
    private int docIndex;

    public List<Article> getArticles() {
        return articles;
    }

    public LAHandler(String nodeName) {
        this.nodeName = nodeName;
    }

    /*
     * 用来标志解析开始
     */
    @Override
    public void startDocument() throws SAXException {
        // TODO Auto-generated method stub
        super.startDocument();
        articles = new ArrayList<Article>();
        //第一行开始
        System.out.println("SAX解析开始");
    }

    @Override
    public void startElement(String uri, String localName, String qName,
                             Attributes attributes) throws SAXException {
        super.startElement(uri, localName, qName, attributes);
        //开始解析book元素的属性

        if (qName.equals("DOC")) {
            article = new Article();
            docIndex++;
            System.out.println("开始遍历第"+docIndex+"本书" + this.nodeName);

            //未知DOC元素下的属性名称及个数 ,目前没用
            int num=attributes.getLength();
            for (int i = 0; i < num; i++) {
                //System.out.print("doc元素的第"+(i+1)+"个属性名："+attributes.getQName(i));
                //System.out.println(" && 属性值："+attributes.getValue(i));
            }
        }else{
            //System.out.print("节点名:"+qName);
        }

        currentTag = qName;
        if (currentTag.equals("HEADLINE") || currentTag.equals("TEXT")){
            currentParentTag = currentTag;
        }

    }



    @Override
    public void characters(char[] ch, int start, int length)
            throws SAXException {
        // TODO Auto-generated method stub
        super.characters(ch, start, length);

        if (currentTag != null ) {
            currentValue = new String(ch, start, length).trim();

            if (currentValue != null && !currentValue.equals("") && !currentValue.equals("\n")) {
                if(currentTag.equals("DOCNO")){
                    article.setDoc_no(currentValue);
                }else if(currentParentTag.equals("HEADLINE") && currentTag.equals("P")){
                    article.setTitle(currentValue);
                    currentParentTag = "";
                }else if(currentParentTag.equals("TEXT") && currentTag.equals("P")){
                    article.setContent(currentValue);
                }else{
                    currentParentTag = "";
                }

            }
        }


        currentTag = null;
        currentValue = null;
    }

    /*
     * 用来遍历xml文件的结束标签
     */
    @Override
    public void endElement(String uri, String localName, String qName)
            throws SAXException {
        super.endElement(uri, localName, qName);
        //是否针对一本书已经遍历结束
        if (qName.equals(nodeName)) {
            articles.add(article);
            System.out.println("添加新文档");

        }
    }



    /*
     * 用来标志解析结束
     */
    @Override
    public void endDocument() throws SAXException {
        // TODO Auto-generated method stub
        super.endDocument();

        //最后一行结束
        System.out.println("SAX解析结束");
    }

}