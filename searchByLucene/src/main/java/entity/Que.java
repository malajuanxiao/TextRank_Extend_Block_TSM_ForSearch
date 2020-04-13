package entity;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class Que {
    private int id;
    private String title;
    private String desc;
    private String narr;
    private List<Result> resultList = new ArrayList<>();
    private Set<String> reply;
    public Que(){}

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDesc() {
        return desc;
    }

    public void setDesc(String desc) {
        this.desc = desc;
    }

    public String getNarr() {
        return narr;
    }

    public void setNarr(String narr) {
        this.narr = narr;
    }

    public List<Result> getResultList() {
        return resultList;
    }

    public void setResultList(List<Result> resultList) {
        this.resultList = resultList;
    }

    public Set<String> getReply() {
        return reply;
    }

    public void setReply(Set<String> reply) {
        this.reply = reply;
    }

    @Override
    public String toString() {
        return "Que{" +
                "id=" + id +
                ", title='" + title + '\'' +
                ", desc='" + desc + '\'' +
                ", narr='" + narr + '\'' +
                ", resultList=" + resultList +
                ", reply=" + reply +
                '}';
    }
}
