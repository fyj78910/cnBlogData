CREATE DATABASE 'cnblogdb';

CREATE TABLE `tb_bloginfo` (
  `Id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `blogdiggnum` int(11) NOT NULL DEFAULT '0' COMMENT '点赞数量',
  `blogtitle` varchar(500) NOT NULL DEFAULT '' COMMENT '博客标题',
  `blogurl` varchar(200) NOT NULL DEFAULT '' COMMENT 'URL',
  `blogauthor` varchar(50) NOT NULL DEFAULT '' COMMENT '作者',
  `blogtime` datetime NOT NULL COMMENT '发布时间',
  `blogcommentnum` int(11) NOT NULL DEFAULT '0' COMMENT '评论数量',
  `blogviewnum` int(11) NOT NULL DEFAULT '0' COMMENT '浏览数量',
  `AddTime` datetime NOT NULL COMMENT '创建时间',
  `blogFId` varchar(50) DEFAULT NULL COMMENT '根据URL生成的ID',
  `blogId` int(11) DEFAULT NULL COMMENT '当前用户发布的博客标识ID',
  `postId` int(11) DEFAULT NULL COMMENT '博客ID',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8

CREATE TABLE `tb_blogdetail` (
  `Id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `blogFId` varchar(50) NOT NULL DEFAULT '' COMMENT 'blogFId',
  `dataType` int(11) NOT NULL DEFAULT '0' COMMENT '类型1分类2标签',
  `dataText` varchar(500) NOT NULL DEFAULT '' COMMENT '内容',
  `AddTime` datetime NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8