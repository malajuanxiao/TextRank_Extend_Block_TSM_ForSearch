package parse;

import entity.Que;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QUHandler extends DefaultHandler {
    private List<Que> querys = null;
    private Que que;
    private String currentTag = null;
    private String currentValue = null;
    private String nodeName = null;
    private int docIndex;
    Pattern r1 = Pattern.compile("Number:(.*)title");
    Pattern r2 = Pattern.compile("title:(.*)desc:");
    Pattern r3 = Pattern.compile("Description:(.*)narr:");
    Pattern r4 = Pattern.compile("desc:(.*)narr:");
    Pattern r5 = Pattern.compile("Narrative:(.*)");
    Pattern r6 = Pattern.compile("narr:(.*)");

    public List<Que> getQuerys() {
        return querys;
    }

    public QUHandler(String nodeName) {
        this.nodeName = nodeName;
    }

    /*
     * 用来标志解析开始
     */
    @Override
    public void startDocument() throws SAXException {
        // TODO Auto-generated method stub
        super.startDocument();
        querys = new ArrayList<Que>();
        //第一行开始
        //System.out.println("SAX解析开始");
    }

    @Override
    public void startElement(String uri, String localName, String qName,
                             Attributes attributes) throws SAXException {
        super.startElement(uri, localName, qName, attributes);
        //开始解析book元素的属性

        if (qName.equals("top")) {
            que = new Que();
            docIndex++;
            System.out.println("开始遍历第"+docIndex+"查询");
            //未知book元素下的属性名称及个数
            int num=attributes.getLength();
            for (int i = 0; i < num; i++) {
                //System.out.print("doc元素的第"+(i+1)+"个属性名："+attributes.getQName(i));
                //System.out.println(" && 属性值："+attributes.getValue(i));
            }
        }
        currentTag = qName;
    }



    @Override
    public void characters(char[] ch, int start, int length)
            throws SAXException {
        // TODO Auto-generated method stub
        super.characters(ch, start, length);



        if (currentTag != null ) {
            currentValue = new String(ch, start, length).trim();
            if (currentValue != null && !currentValue.equals("") && !currentValue.equals("\n")) {
                Matcher m1 = r1.matcher(currentValue);
                if (m1.find()){
                    que.setId(Integer.parseInt(m1.group(1).trim()));
                }
                m1 = r2.matcher(currentValue);
                if (m1.find()){
                    que.setTitle(m1.group(1).trim());
                }
                m1 = r3.matcher(currentValue);
                Matcher m2 = r4.matcher(currentValue);
                if (m1.find()){
                    que.setDesc(m1.group(1).trim());
                }else if(m2.find()){
                    que.setDesc(m2.group(1).trim());
                }
                m1 = r5.matcher(currentValue);
                m2 = r6.matcher(currentValue);
                if (m1.find()){
                    que.setNarr(m1.group(1).trim());
                }else if(m2.find()){
                    que.setDesc(m2.group(1).trim());
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
            querys.add(que);
            System.out.println("添加新测试查询,共"+querys.size()+"条");

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
        //System.out.println("SAX解析结束");
    }
}
